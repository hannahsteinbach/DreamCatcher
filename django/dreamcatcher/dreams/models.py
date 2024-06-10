from django.db import models
from django.contrib.auth.models import User


class Dream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()
    shared = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
