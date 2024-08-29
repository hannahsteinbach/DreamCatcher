from django import forms
from .models import Dream, Comment
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import TimeInput
from django.contrib.auth.models import User
from datetime import date
from .models import Profile, Questionnaire


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ChoiceField(
        choices=Profile._meta.get_field('avatar').choices,
        widget=forms.RadioSelect
    )
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']


class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = ['stress', 'creativity', 'sleep_duration', 'sleep_quality', 'awakening', 'morning_mood',
        'dream_relation_oneself', 'dream_impact_mood', 'notes']

        labels = {
            'stress': 'Have you been feeling stressed lately?',
            'creativity': 'Are you feeling more creative?',
            'sleep_duration': 'How long did you sleep yesterday?',
            'sleep_quality': 'How did you sleep last night?',
            'awakening': 'Did you wake up because of your dream?',
            'morning_mood': 'Did your dream affect your mood the next morning?',
            'dream_relation_oneself': 'Is this dream directly related to you (any real-life experience associated with it)?',
            'dream_impact_mood': 'Did your dream affect your mood the days after?',
            'notes': 'Any notes about your dream (how it affected your mood, how it is related to your waking life)?',
        }

        widgets = {
            'stress': forms.Select(attrs={'class': 'form-control'}),
            'creativity': forms.Select(attrs={'class': 'form-control'}),
            'sleep_duration': forms.Select(attrs={'class': 'form-control'}),
            'sleep_quality': forms.Select(attrs={'class': 'form-control'}),
            'awakening': forms.Select(attrs={'class': 'form-control'}),
            'morning_mood': forms.Select(attrs={'class': 'form-control'}),
            'dream_relation_oneself': forms.Select(attrs={'class': 'form-control'}),
            'dream_impact_mood': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


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