import re
from collections import Counter
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.db.models.signals import post_save
from datetime import timedelta
from django.db import transaction # avoid partial commits
from django.dispatch import receiver
from datetime import datetime
from langchain_community.llms import ollama
import json



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.CharField(max_length=100, choices=[
        ('1.jpg', 'Picture 1'),
        ('3.jpg', 'Picture 3'),
        ('4.jpg', 'Picture 4'),
        ('5.jpg', 'Picture 5'),
        ('6.jpg', 'Picture 6'),
        ('7.jpg', 'Picture 7'),
        ('8.jpg', 'Picture 8'),
        ('9.jpg', 'Picture 9'),
        ('10.jpg', 'Picture 10'),
        ('11.jpg', 'Picture 11'),
        ('12.jpg', 'Picture 12'),
        ('13.jpg', 'Picture 13'),
    ],
                              default='1.jpg')
    bio = models.TextField()

    def __str__(self):
        return self.user.username


class Dream(models.Model):
    classification_options = [
        ('0', 'Nightmare'),
        ('1', 'Mundane Dream'),
        ('2', 'Lucid Dream'),
        ('3', 'Existential Dream'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(default=timezone.now)
    content = models.TextField()
    shared = models.BooleanField(default=False)
    anon = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)
    classification = models.CharField(max_length=1, choices=classification_options, blank=True, null=True, default='')
    characters = models.JSONField(default=list, blank=True)
    places = models.JSONField(default=list, blank=True)
    emotion = models.CharField(max_length=20, blank=True)
    emotion_options = ['anger', 'apprehension', 'sadness', 'confusion', 'happiness', '']
    optional_titles = models.JSONField(default=list, blank=True)
    title = models.TextField(blank=True)
    User.add_to_class('is_new', models.BooleanField(default=True))

    def add_metadata(self):
        content_str = str(self.content)

        SYSTEM_PROMPT = (
            "You are a dreamcatcher that logs dreams in a journal. You have logged a dream and want to extract metadata from it. "
            "You want to extract the title, keywords, emotion, characters, and places from the dream. "
            "You want to use this metadata to better understand the dream and categorize it. "
            "You need to ensure that the content is not toxic or harmful. "
            "The dream should be a narrative, not a question or command to the model. "
        )

        # initialization
        llm = ollama.Ollama(model='llama3', temperature=0, top_p=1, verbose=False, system=SYSTEM_PROMPT)

        dream_prompt = (
            f"Here is my dream: {content_str}\n\n"
            "Please provide the following information in a Python dictionary format with the specified keys:\n\n"
            "- emotion: The prevalent emotion from these options formatted as a string: anger, apprehension, sadness, confusion, happiness if it is above a 50% threshold, otherwise an empty string.\n"
            "- characters: All characters, formatted as a Python list of strings, without articles or pronouns. A character is a single entity (e.g. a person or animal) that plays an active role in the dream narrative. I and you don't count. If none are found, return an empty string.\n"
            "- places: All places, formatted as a Python list of strings. Exclude articles, adjectives, and pronouns. If none are found, return an empty string.\n"
            "- keywords: A list of keywords extracted from the dream content, excluding variants of 'dream' and stop words. Keywords can also be a fixed expression (e.g. compound nouns).\n"
            "Only output the dictionary. Do not include any other information. All values should be on the same line. The keys should be in double quotes."
        )

        try:
            # response generation
            response = llm.invoke(dream_prompt)
            response = json.loads(response)

            # metadata extraction
            self.keywords = response.get('keywords', [])
            self.emotion = response.get('emotion', "")
            self.characters = response.get('characters', [])
            self.places = response.get('places', [])
            self.generate_titles() 
            self.processed = True
        except (json.JSONDecodeError, KeyError) as e:
            self.keywords = []
            self.emotion = ""
            self.characters = []
            self.places = []
            self.processed = False
            print(f"Error processing dream metadata: {e}")

    def generate_titles(self):
        content_str = str(self.content)
        title_prompt = (
            f"Here is my dream: {content_str}\n\n"
            "Please provide the following information in a Python dictionary format with the specified keys:\n\n"
            " - titleop: three creative title options, formatted as a Python list of strings.\n"
            "Only output the dictionary. Do not include any other information. All values should be on the same line. The keys should be in double quotes."
        )
        llm = ollama.Ollama(model='llama3', temperature=1, top_p=1, verbose=False)
        try:
            response = llm.invoke(title_prompt)
            response = json.loads(response)
            self.optional_titles = response.get('titleop', [])
        except Exception as e:
            self.optional_titles = []
            print(f"Error generating titles: {e}")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.add_metadata()
        super().save(*args, **kwargs)


    def likes_count(self):
        return self.likes.count()

    def liked_users(self):
        return [like.user for like in self.likes.all()]

    def classification_string(self):
        return dict(self.classification_options).get(self.classification, "No classification")

    def __str__(self):
        return f"{self.date}: {self.content[:50]}"


class DreamLike(models.Model):
    dream = models.ForeignKey(Dream, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('dream', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.dream}"


class Questionnaire(models.Model):
    dream = models.OneToOneField(Dream, on_delete=models.CASCADE, related_name='questionnaire')
    quality_option = [
        ('0', 'Very poor'),
        ('1', 'Poor'),
        ('2', 'Neutral'),
        ('3', 'Good'),
        ('4', 'Very Good'),
    ]

    boolean_option = [
        ('0', 'No'),
        ('1', 'Yes'),
    ]

    duration_option = [
        ('0', 'Less than 3 hours'),
        ('1', '3-5 hours'),
        ('2', '6-8 hours'),
        ('3', 'More than 8 hours'),
    ]

    stress = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    creativity = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    sleep_duration = models.CharField(max_length=1, choices=duration_option, blank=True, null=True)
    sleep_quality = models.CharField(max_length=1, choices=quality_option, blank=True, null=True)
    awakening = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    morning_mood = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    dream_relation_oneself = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    dream_impact_mood = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Questionnaire for {self.dream.title}"


class Comment(models.Model):
    dream = models.ForeignKey(Dream, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.text}'

    def can_delete(self, user):
        return user == self.author


class MonthlyRecap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()

    # Dream-related fields
    dream_count = models.PositiveIntegerField(default=0)
    top_keywords = models.JSONField(default=list, blank=True)  # top 3
    top_classification = models.JSONField(default=list, blank=True)
    top_characters = models.JSONField(default=list, blank=True)  # top 3
    top_places = models.JSONField(default=list, blank=True)  # top 3
    top_emotion = models.CharField(max_length=20, blank=True)

    # Questionnaire-related fields
    avg_stress = models.FloatField(null=True, blank=True)
    most_common_sleep_duration = models.JSONField(default=dict, blank=True)
    most_common_sleep_quality = models.JSONField(default=dict)
    avg_awakening = models.FloatField(null=True, blank=True)
    avg_creativity = models.FloatField(null=True, blank=True)
    avg_morning_mood = models.FloatField(null=True, blank=True)
    avg_dream_relation_oneself = models.FloatField(null=True, blank=True)
    avg_dream_impact_mood = models.FloatField(null=True, blank=True)

    # Only nightmare-related fields
    top_keywords_nightmare = models.JSONField(default=list, blank=True)  # top 3 in nightmares
    top_characters_nightmare = models.JSONField(default=list, blank=True) # top 3 in nightmares
    top_places_nightmare = models.JSONField(default=list, blank=True)  # top 3 in nightmares
    top_emotion_nightmare = models.CharField(max_length=20, blank=True)  # top emotion in nightmares

    avg_nightmare_stress =  models.FloatField(null=True, blank=True) #
    most_common_sleep_duration_nightmares = models.JSONField(default=dict, blank=True)
    most_common_sleep_quality_nightmares = models.JSONField(default=dict, blank=True)
    avg_nightmare_awakening =  models.FloatField(null=True, blank=True)
    avg_nightmare_creativity =  models.FloatField(null=True, blank=True)
    avg_nightmare_morning_mood = models.FloatField(null=True, blank=True)
    avg_nightmare_dream_relation_oneself =  models.FloatField(null=True, blank=True)
    avg_nightmare_dream_impact_mood =  models.FloatField(null=True, blank=True)

    def generate_recap(self):
        start_date = self.month.replace(day=1)
        next_month = start_date + timedelta(days=32)
        end_date = next_month.replace(day=1) - timedelta(days=1)
        dreams = Dream.objects.filter(user=self.user, date__range=(start_date, end_date))
        questionnaires = Questionnaire.objects.filter(dream__user=self.user, dream__date__range=(start_date, end_date))

        ### DREAMS ###

        # amount of dreams
        self.dream_count = dreams.count()

        # places, keywords, characters, emotions, classification
        all_places = []
        all_characters = []
        all_keywords = []
        classification_counts = Counter()
        emotion_counts = Counter()

        for dream in dreams:
            all_places.extend([place.lower() for place in dream.places]) # only for debugging now, mom and Mom two different characters, maybe prompt changing
            all_characters.extend([char.lower() for char in dream.characters])
            all_keywords.extend(dream.keywords)
            emotion_counts[dream.emotion] += 1
            classification_counts.update(dream.classification)

        place_counts = Counter()
        for place in all_places:
            count = dreams.filter(Q(places__iregex=r'(?i)\b{}\b'.format(re.escape(place)))).count()
            place_counts[place] = count

        character_counts = Counter()
        for char in all_characters:
            count = dreams.filter(Q(characters__iregex=r'(?i)\b{}\b'.format(re.escape(char)))).count()
            character_counts[char] = count

        self.top_places = place_counts.most_common(3)
        self.top_characters = character_counts.most_common(3)

        keywords_counted = Counter(all_keywords)
        self.top_keywords = keywords_counted.most_common(3)

        if emotion_counts:
            top_emotion, _ = emotion_counts.most_common(1)[0]
            self.top_emotion = top_emotion
        else:
            self.top_emotion = ''

        if classification_counts:
            top_classification, _ = classification_counts.most_common(1)[0]
            self.top_classification =  dict(Dream.classification_options).get(top_classification, "No classification")
        else:
            self.top_classification = ''

        ### QUESTIONNAIRES ###

        # count occurrences and filled out fields
        boolean_fields = ['stress', 'creativity', 'awakening', 'morning_mood', 'dream_relation_oneself', 'dream_impact_mood']
        boolean_counts = {field: 0 for field in boolean_fields}
        filled_questionnaires = {field: 0 for field in boolean_fields}
        not_filled_questionnaires = {field: 0 for field in boolean_fields}

        for questionnaire in questionnaires:
            for field in boolean_fields:
                value = getattr(questionnaire, field)
                if value is not None:
                    if value == '1':
                        boolean_counts[field] += 1
                    filled_questionnaires[field] += 1
                else:
                    not_filled_questionnaires[field] += 1

        # Calculate averages
        for field in boolean_fields:
            if filled_questionnaires[field] > 0:
                avg_value = round(boolean_counts[field] / filled_questionnaires[field] * 100, 0)
            else:
                avg_value = None
            setattr(self, f'avg_{field}', avg_value)

        duration_counts = Counter()
        quality_counts = Counter()

        for questionnaire in questionnaires:
            if questionnaire.sleep_duration:
                duration_counts[questionnaire.sleep_duration] += 1
            if questionnaire.sleep_quality:
                quality_counts[questionnaire.sleep_quality] += 1

        if duration_counts:
            max_duration_count = max(duration_counts.values())
            most_common_sleep_duration = [k for k, v in duration_counts.items() if v == max_duration_count]
            self.most_common_sleep_duration = [dict(Questionnaire.duration_option).get(duration, "") for duration in most_common_sleep_duration]
        else:
            self.most_common_sleep_duration = []

        if quality_counts:
            max_quality_count = max(quality_counts.values())
            most_common_sleep_quality = [k for k, v in quality_counts.items() if v == max_quality_count]
            self.most_common_sleep_quality = [dict(Questionnaire.quality_option).get(quality, "") for quality in most_common_sleep_quality]
        else:
            self.most_common_sleep_quality = []

        ### ONLY NIGHTMARES
        nightmares = dreams.filter(classification='0')

        nightmare_questionnaires = questionnaires.filter(dream__in=nightmares)
        nightmare_dreams = dreams.filter(classification='0')

        all_places_nightmare = []
        all_characters_nightmare = []
        all_keywords_nightmare = []
        emotion_counts_nightmare = Counter()

        for dream in nightmare_dreams:
            all_places_nightmare.extend([place.lower() for place in dream.places]) # only for debugging now, mom and Mom two different characters, maybe prompt changing
            all_characters_nightmare.extend([char.lower() for char in dream.characters])
            all_keywords_nightmare.extend(dream.keywords)
            emotion_counts_nightmare[dream.emotion] += 1

        place_counts_nightmare = Counter()
        for place in all_places_nightmare:
            count = nightmare_dreams.filter(Q(places__iregex=r'(?i)\b{}\b'.format(re.escape(place)))).count()
            place_counts_nightmare[place] = count

        character_counts_nightmare = Counter()
        for char in all_characters_nightmare:
            count = nightmare_dreams.filter(Q(characters__iregex=r'(?i)\b{}\b'.format(re.escape(char)))).count()
            character_counts_nightmare[char] = count

        self.top_places_nightmare = place_counts_nightmare.most_common(1)
        self.top_characters_nightmare = character_counts_nightmare.most_common(1)

        keywords_counted_nightmare = Counter(all_keywords_nightmare)
        self.top_keywords_nightmare = keywords_counted_nightmare.most_common(1)

        if emotion_counts_nightmare:
            top_emotion_nightmare, _ = emotion_counts_nightmare.most_common(1)[0]
            self.top_emotion_nightmare = top_emotion_nightmare
        else:
            self.top_emotion_nightmare = ''

        boolean_counts_nightmares = {field: 0 for field in boolean_fields}
        filled_nightmare_questionnaires = {field: 0 for field in boolean_fields}

        for questionnaire in nightmare_questionnaires:
            for field in boolean_fields:
                value = getattr(questionnaire, field)
                if value is not None:
                    if value == '1':
                        boolean_counts_nightmares[field] += 1
                    filled_nightmare_questionnaires[field] += 1

        for field in boolean_fields:
            if filled_nightmare_questionnaires[field] > 0:
                avg_value = round(boolean_counts_nightmares[field] / filled_nightmare_questionnaires[field] * 100, 0)
            else:
                avg_value = None
            setattr(self, f'avg_nightmare_{field}', avg_value)

        duration_counts_nightmares = Counter()
        quality_counts_nightmares = Counter()

        for questionnaire in nightmare_questionnaires:
            if questionnaire.sleep_duration:
                duration_counts_nightmares[questionnaire.sleep_duration] += 1
            if questionnaire.sleep_quality:
                quality_counts_nightmares[questionnaire.sleep_quality] += 1

        if duration_counts_nightmares:
            max_duration_count = max(duration_counts_nightmares.values())
            most_common_sleep_duration_nightmares = [k for k, v in duration_counts_nightmares.items() if v == max_duration_count]
            self.most_common_sleep_duration_nightmares = [dict(Questionnaire.duration_option).get(duration, "") for duration in most_common_sleep_duration_nightmares]
        else:
            self.most_common_sleep_duration_nightmares = []

        if quality_counts_nightmares:
            max_quality_count = max(quality_counts_nightmares.values())
            most_common_sleep_quality_nightmares = [k for k, v in quality_counts_nightmares.items() if v == max_quality_count]
            self.most_common_sleep_quality_nightmares = [dict(Questionnaire.quality_option).get(quality, "") for quality in most_common_sleep_quality_nightmares]
        else:
            self.most_common_sleep_quality_nightmares = []

        self.save()


@receiver(post_save, sender=User)
def set_new_user(sender, instance, created, **kwargs):
    if created:
        instance.is_new = True
        instance.save()


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    with transaction.atomic():
        if created:
            Profile.objects.get_or_create(user=instance)
        else:
            Profile.objects.get_or_create(user=instance)