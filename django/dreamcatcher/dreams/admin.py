from django.contrib import admin
from .models import Dream, Comment, DreamLike, Profile

# Register your models here.
admin.site.register(Dream)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(DreamLike)
