from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from langchain_community.llms import ollama
import json

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
            f"You are a dreamcatcher who logs dreams in a journal. You have logged a dream and want to extract metadata from it. "
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
            "- keywords: A list of 5 keywords extracted from the dream content, excluding variants of 'dream' and stop words. Only include words from the dream itself. You don't have to include exactly 5 words if the dream is too short or the keywords are not interesting enough. Keywords can also be a fixed expression (e.g. compound nouns). Anything that has already been identified as a character or a place should not be a keyword.\n"
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
       # add_dream_to_collection(self.id, self.content) -> added this to log_dream, well see

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


class Comment(models.Model):
    dream = models.ForeignKey(Dream, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.text}'

    def can_delete(self, user):
        return user == self.author


@receiver(post_save, sender=User)
def set_new_user(sender, instance, created, **kwargs):
    if created:
        instance.is_new = True
        instance.save()