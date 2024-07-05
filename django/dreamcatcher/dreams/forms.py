from django import forms
from .models import Dream, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.migrations.state import get_related_models_tuples
from django.utils.translation import gettext_lazy as _

class DreamForm(forms.ModelForm):
    class Meta:
        model = Dream
        fields = ['date', 'content', 'classification']



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')