from django.db import models
from django.contrib.auth.models import User


class Dream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    shared = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date}: {self.content[:50]}"