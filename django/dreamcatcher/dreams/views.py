from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .forms import SignUpForm
import logging

logger = logging.getLogger(__name__)



def home(request):
    return render(request, 'dreams/home.html')


@login_required
def log_dream(request):
    return render(request, 'dreams/log_dream.html')


@login_required
def questionnaires(request):
    return render(request, 'dreams/questionnaires.html')


@login_required
def dream_journal(request):
    return render(request, 'dreams/dream_journal.html')


@login_required
def personal_statistics(request):
    return render(request, 'dreams/personal_statistics.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out. Sweet Dreams 🌙')
    return redirect('dreams:home')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            logger.info("Form data: %s", form.cleaned_data)

            user = form.save()
            user.refresh_from_db()
            user.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, 'Your account was created successfully!')
            return redirect('dreams:home')
        else:
            logger.error("Form errors: %s", form.errors)
            if 'password2' in form.errors:
                messages.error(request, 'Passwords do not match. Please try again.')
            if 'email' in form.errors:
                if 'unique' in form.errors['email']:
                    messages.error(request, 'Email address is already in use.')
                else:
                    messages.error(request, 'Invalid email address. Please enter a valid email.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
