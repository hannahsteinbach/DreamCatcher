from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from .forms import SignUpForm, DreamForm
import logging
from django.shortcuts import render, redirect
from .models import Dream
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import F
from django.db.models import Q
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

def home(request):
    if request.user.is_authenticated:
        return redirect('dreams:home_logged_in')
    return render(request, 'base_generic.html')

def aboutus(request):
    return render(request, 'aboutus.html')

@login_required
def home_logged_in(request):
    messages.success(request, f'Welcome, {request.user.username}! Let\'s take a journey into your subconscious 🗺️')
    return render(request, 'home.html')

@login_required
def log_dream(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user
        dream = Dream.objects.create(
            user=user,
            date=date.today(),
            content=content,
            shared=False,
            processed=False
        )
        dream.save()
        messages.success(request, 'Your dream was successfully saved!')
        return render(request, 'dreams/log_dream.html')
    return render(request, 'dreams/log_dream.html')


@login_required
def delete_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    if request.method == 'POST':
        dream.delete()
        messages.success(request, 'Dream deleted successfully!')
    return redirect('dreams:dream_journal')

@login_required
def edit_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    if request.method == 'POST':
        form = DreamForm(request.POST, instance=dream)
        if form.is_valid():
            form.save()
            return redirect('dreams:dream_journal')
    else:
        form = DreamForm(instance=dream)
    return render(request, 'dreams/edit_dream.html', {'form': form})

@login_required
def add_to_favorites(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    dream.is_favorite = True
    dream.save()
    return redirect('dreams:dream_journal')


@login_required
def questionnaires(request):
    return render(request, 'dreams/questionnaires.html')

@login_required
def dream_journal(request):
    query = request.GET.get('q')
    if query:
        dreams = Dream.objects.filter(
            Q(content__icontains=query) | Q(date__icontains=query)
        ).order_by('-date')
    else:
        dreams = Dream.objects.all().order_by('-date')
    return render(request, 'dreams/dream_journal.html', {'dreams': dreams, 'query': query})

@login_required
def personal_statistics(request):
    return render(request, 'dreams/personal_statistics.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out. Sweet Dreams 🌙')
    return redirect('home')

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
            return redirect('dreams:home_logged_in')
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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
