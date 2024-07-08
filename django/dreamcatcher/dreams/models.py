from django.db import models
from django.contrib.auth.models import User
from langchain_community.llms import ollama
from django.contrib.auth import get_user_model
import json

class Dream(models.Model):
    classification_options = [
        ('0', 'Nightmare'),
        ('1', 'Mundane Dream'),
        ('2', 'Lucid Dream'),
        ('3', 'Existential Dream'),
        ('4', 'None'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    shared = models.BooleanField(default=False)
    anon = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)
    classification = models.CharField(max_length=1, choices=classification_options, blank=True, null=True, default='4')
    characters = models.JSONField(default=list, blank=True)
    places = models.JSONField(default=list, blank=True)
    emotion = models.CharField(max_length=20, blank=True)
    #titles = models.JSONField(default=list, blank=True)

    def add_metadata(self):
        content_str = str(self.content)

        # initialization
        llm = ollama.Ollama(model='llama3', temperature=0, top_p=1, verbose=False)

        dream_prompt = (
            f"This is my dream: {content_str}\n\n"
            "Please provide the following information in a Python dictionary format with the specified keys:\n\n"
            "- titles: Three title options to choose from, formatted as a Python list of strings.\n"
            "- keywords: A list of exactly 5 keywords extracted from the dream content, excluding variants of 'dream' and stop words.\n"
            "- emotion: The prevalent emotion from these options formatted as a list: anger, apprehension, sadness, confusion, happiness if it is above a 60% threshold, otherwise an empty string.\n"
            "- characters: All characters found in the dream, formatted as a Python list of strings.\n"
            "- places: All places mentioned in the dream, formatted as a Python list of strings.\n"
            "Only output the dictionary. Do not include any other information. All values should be on the same line. The keys should be in double quotes."
        )

        # response generation
        response = llm.invoke(dream_prompt)
        response = json.loads(response)

        # metadata extraction
        #self.titles = response.get('titles', [])
        self.keywords = response.get('keywords', [])
        self.emotion = response.get('emotion', [])
        self.characters = response.get('characters', [])
        self.places = response.get('places', [])
        self.processed = True

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


class Comment(models.Model):
    dream = models.ForeignKey(Dream, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.text}'

    def can_delete(self, user):
        return user == self.author