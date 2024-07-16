from django.contrib import admin
from .models import Dream, Comment, DreamLike

# Register your models here.
admin.site.register(Dream)
admin.site.register(Comment)
admin.site.register(DreamLike)
