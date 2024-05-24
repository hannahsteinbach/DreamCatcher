from django.db import models
from django.contrib.auth.models import User


class Dream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    shared = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)


class DreamAnalysis(models.Model):
    dream = models.OneToOneField(Dream, on_delete=models.CASCADE)
    emotional_valence = models.FloatField()
    topics = models.TextField()
    genre = models.CharField(max_length=100)
    level_of_realism = models.FloatField()
    recurring_characters = models.TextField()
    themes = models.TextField()