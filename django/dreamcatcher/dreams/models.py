from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
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
            "You are a dreamcatcher who logs dreams in a journal. You have logged a dream and want to extract metadata from it. "
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
            "- titleop: Three creative title options, formatted as a Python list of strings.\n"
            "- emotion: The prevalent emotion from these options formatted as a string: anger, apprehension, sadness, confusion, happiness if it is above a 50% threshold, otherwise an empty string.\n"
            "- characters: All characters, formatted as a Python list of strings, without articles or pronouns. A character is a single entity (e.g. a person or animal) that plays an active role in the dream narrative. I and you don't count. If none are found, return an empty string.\n"
            "- places: All places, formatted as a Python list of strings, without articles. If none are found, return an empty string.\n"
            "- keywords: A list of keywords extracted from the dream content, excluding variants of 'dream' and stop words. Keywords can also be a fixed expression (e.g. compound nouns).\n"
            "Only output the dictionary. Do not include any other information. All values should be on the same line. The keys should be in double quotes."
        )

        try:
            # response generation
            response = llm.invoke(dream_prompt)
            response = json.loads(response)

            # metadata extraction
            self.optional_titles = response.get('titleop', [])
            self.keywords = response.get('keywords', [])
            self.emotion = response.get('emotion', "")
            self.characters = response.get('characters', [])
            self.places = response.get('places', [])
            self.processed = True
        except (json.JSONDecodeError, KeyError) as e:
            self.optional_titles = []
            self.keywords = []
            self.emotion = ""
            self.characters = []
            self.places = []
            self.processed = False
            print(f"Error processing dream metadata: {e}")

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

'''
class MonthlyRecap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()

    # Dream-related
    # milestones?
    dream_count = models.PositiveIntegerField(default=0)
    is_favorite = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)  # Most common keywords (TOP 3)
    classification = models.CharField(max_length=1, choices=classification_options, blank=True, null=True, default='')  # Most common type of dream
    characters = models.JSONField(default=list, blank=True)  # Most common characters (TOP 3)
    places = models.JSONField(default=list, blank=True)  # Most common places (TOP 3)
    emotion = models.CharField(max_length=20, blank=True)  # Most common emotion

    # Questionnaire-related
    avg_stress = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True) #(on what days with high stress did u have nightmares or vice versa)
    avg_sleep_duration = models.CharField(max_length=1, choices=duration_option, blank=True, null=True)
    avg_sleep_quality = models.CharField(max_length=1, choices=quality_option, blank=True, null=True)
    count_awakening = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    count_creativity = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    count_morning_mood = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    count_dream_relation_oneself = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    count_dream_impact_mood = models.CharField(max_length=1, choices=boolean_option, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Social media-related
    total_likes_received = models.PositiveIntegerField(default=0)
    total_likes_given = models.PositiveIntegerField(default=0)
    total_comments_given = models.PositiveIntegerField(default=0)
    total_comments_received = models.PositiveIntegerField(default=0)
'''

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