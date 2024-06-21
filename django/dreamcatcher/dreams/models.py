from django.db import models
from django.contrib.auth.models import User
from keybert import KeyBERT
import json
import re


class Dream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    shared = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):

        content_str = str(self.content)

        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(content_str, keyphrase_ngram_range=(1, 1),
                                             top_n=5, stop_words=None)
        #top_n: how many keywords should be extracted?
        #keyphrase_ngram_range: how long should the keyphrases be? (i think only one should be good)
        #can also add more, e.g. how diverse the results should be

        self.keywords = [keyword[0] for keyword in keywords if not
                         re.compile(r'dream(ed|t)?', re.IGNORECASE).match(keyword[0])]

        super().save(*args, **kwargs)

    def likes_count(self):
        return self.likes.count()

    def liked_users(self):
        return [like.user for like in self.likes.all()]

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
