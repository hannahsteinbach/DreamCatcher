from django.db import models
from django.contrib.auth.models import User
from keybert import KeyBERT
import json
import dreamy
import re


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
    processed = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    keywords = models.JSONField(default=list, blank=True)
    classification = models.CharField(max_length=1, choices=classification_options, blank=True, null=True, default='4')
    persons = models.JSONField(default=list, blank=True)
    emotion = models.CharField(max_length=20, blank=True)

    def add_metadata(self):
        content_str = str(self.content)

        # Extract keywords using KeyBERT
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(
            content_str,
            keyphrase_ngram_range=(1, 1),
            top_n=5,
            stop_words='english',
            use_mmr=True,
            diversity=0.7
        )
        # top_n: how many keywords should be extracted?
        # keyphrase_ngram_range: how long should the keyphrases be? (i think only one should be good)
        # can also add more, e.g. how diverse the results should be
        # use_mmr: Maximal Margin Relevance, based on cosine similarity
        # diversity: how diverse should the key words be? (what do you think)
        # before adding use_mmr and diversity: Ted dream: ted, tears, bulgarian, crying
        # afterwards: ted tears bulgarian souvenir
        # all information on keybert: https://github.com/MaartenGr/KeyBERT

        self.keywords = [keyword[0] for keyword in keywords if
                         not re.compile(r'dream(ed|t)?', re.IGNORECASE).match(keyword[0])]

        # Sentiment Analysis and Named Entity Recognition, using DReamY
        reports = [content_str]
        sentiment = "SA"
        persons = "NER"
        batch_size = 16
        device = "cpu"

        SA_predictions = dreamy.annotate_reports(
            reports,
            task=sentiment,
            device=device,
            batch_size=batch_size,
        )

        NER_predictions = dreamy.annotate_reports(
            reports,
            task=persons,
            device=device,
            batch_size=batch_size,
        )

        # Get the emotion with highest score
        max_score = 0
        for sentiment in SA_predictions[0]:
            if sentiment['score'] > max_score:
                max_score = sentiment['score']
                highest_label = sentiment['label']

        # Get emotion to label
        sentiment_lookup = {
            "AN": "Anger",
            "AP": "Apprehension",
            "SD": "Sadness",
            "CO": "Confusion",
            "HA": "Happiness"
        }
        self.emotion = sentiment_lookup[highest_label]

        # Get persons according to Van de Castle
        self.persons = [person for person in NER_predictions]

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
