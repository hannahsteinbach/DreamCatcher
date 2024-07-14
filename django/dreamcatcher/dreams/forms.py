from django import forms
from .models import Dream, Comment
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import TimeInput
from django.contrib.auth.models import User
from datetime import date


class DreamForm(forms.ModelForm):
    current_day = date.today()
    current_year = current_day.year
    date = forms.DateField(label='Date', widget=forms.SelectDateWidget(years=range(1970, current_year+1)), required=False)

    class Meta:
        model = Dream
        fields = ['date', 'content', 'classification']


class DateForm(forms.ModelForm):
    current_day = date.today()
    current_year = current_day.year
    date = forms.DateField(label='Date', widget=forms.SelectDateWidget(years=range(1970, current_year+1)), required=False)
    time = forms.TimeField(label='Time', widget=TimeInput(format='%H:%M'), required=False)

    class Meta:
        model = Dream
        fields = ['date', 'time']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class TitleForm(forms.ModelForm):
    class Meta:
        model = Dream
        fields = ['optional_titles', 'title']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')