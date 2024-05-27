from django import forms
from .models import Dream
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DreamForm(forms.ModelForm):
    class Meta:
        model = Dream
        fields = ['date', 'content', 'shared']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')