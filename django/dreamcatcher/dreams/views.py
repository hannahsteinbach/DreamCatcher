from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.views.generic.detail import DetailView
from django.http import HttpResponseForbidden
from .forms import SignUpForm, DreamForm, CommentForm, DateForm, TitleForm
import logging
from django.shortcuts import render, redirect
from .models import Dream, DreamLike, Comment
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import F
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import get_object_or_404
from collections import Counter
import re
from django.db.models import Count
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

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
        classification = request.POST.get('classification')
        user = request.user

        dream = Dream.objects.create(
            user=user,
            date=date.today(),
            content=content,
            shared=False,
            processed=False,
            classification=classification
        )

        form = DateForm(request.POST, instance=dream)
        if form.is_valid():

            dream_date = form.cleaned_data['date']

            if not dream_date:
                dream_date = date.today()

            if dream_date > date.today():
                form.add_error('date', 'The date cannot be in the future.')
            elif dream_date < date(1970, 1, 1):
                form.add_error('date', 'The date cannot be earlier than 1970.')

            if not form.errors:
                dream.date = dream_date
                dream.save()
                return redirect('dreams:choose_title', dream_id=dream.id)
        else:
            messages.error(request, "Failed to log your dream. Please correct the errors below.")

    else:
        form = DateForm(initial={'date': date.today()})

    return render(request, 'dreams/log_dream.html', {'form': form})


@login_required
def choose_title(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    optional_titles = dream.optional_titles
    if not optional_titles:
        dream.delete()
    else:
        if request.method == 'POST':
            selected_title = request.POST.get('title')
            if selected_title:
                dream.title = selected_title
                dream.save()
                messages.success(request, 'Great choice!')
                if not dream.emotion:
                    return redirect('dreams:choose_emotion', dream_id=dream.id)
                else:
                    return redirect('dreams:dream_journal')
            else:
                messages.error(request, 'Please select a title.')
    return render(request, 'dreams/choose_title.html', {'dream': dream})

@login_required
def choose_emotion(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    if request.method == 'POST':
        selected_emotion = request.POST.get('emotion')
        dream.emotion = selected_emotion
        dream.save()
        return redirect('dreams:dream_journal')
    return render(request, 'dreams/choose_emotion.html', {'dream': dream})


@login_required
def delete_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.delete()
    return redirect('dreams:dream_journal')


@login_required
def edit_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    dream_bc = dream.content

    if request.method == 'POST':
        form = DreamForm(request.POST, instance=dream)
        if form.is_valid():
            dream_ac = form.cleaned_data['content']
            dream_date = form.cleaned_data['date']
            dream_time = form.cleaned_data.get('time', dream.time)
            if dream_date > date.today():
                form.add_error('date', 'The date cannot be in the future.')
            elif dream_date < date(1970, 1, 1):
                form.add_error('date', 'The date cannot be earlier than 1970.')

            if not form.errors:
                dream.date = dream_date
                dream.time = dream_time
                dream.classification = form.cleaned_data['classification']
                if dream_bc != dream_ac:
                    dream.content = dream_ac
                    dream.add_metadata()  # only generate metadata again if content was changed
                dream.save()
                return redirect('dreams:dream_journal')

    else:
        form = DreamForm(instance=dream)

    return render(request, 'dreams/edit_dream.html', {'form': form})

@login_required
def add_to_favorites(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.is_favorite = True
    dream.save(update_fields=['is_favorite'])
    messages.success(request, 'Dream was successfully added to favorites!')
    # all messages dont work
    return redirect(request.META.get('HTTP_REFERER', 'dreams:dream_journal'))


@login_required
def remove_from_favorites(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.is_favorite = False
    dream.save(update_fields=['is_favorite'])
    messages.success(request, 'Dream was successfully removed from favorites!')
    return redirect(request.META.get('HTTP_REFERER', 'dreams:dream_journal'))

@login_required
def share_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.shared = True
    dream.anon = False
    dream.save(update_fields=['shared'])
    dream.save(update_fields=['anon'])
    messages.success(request, 'Dream shared successfully!')
    return redirect('dreams:dream_journal')

@login_required
def share_dream_anon(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.shared = True
    dream.anon = True
    dream.save(update_fields=['shared'])
    dream.save(update_fields=['anon'])
    messages.success(request, 'Dream shared successfully!')
    return redirect('dreams:dream_journal')

@login_required
def unshare_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.shared = False
    dream.save(update_fields=['shared'])
    messages.success(request, 'Dream unshared successfully!')
    return redirect('dreams:dream_journal')


@login_required
def gallery(request):
    query = request.GET.get('q', '')
    dreams = Dream.objects.filter(shared=True)
    class_query = request.GET.get('classification', '')
    emotion_query = request.GET.get('emotion', '')
    keyword_query = request.GET.get('keyword', '')
    character_query = request.GET.get('character', '')
    place_query = request.GET.get('place', '')

    for dream in dreams:
        dream.is_liked_by_user = DreamLike.objects.filter(user=request.user, dream=dream).exists()

    if query:
        dreams = dreams.filter(Q(content__iregex=r'\b{}\b'.format(re.escape(query))))  # query for whole word

    if class_query:
        dreams = dreams.filter(classification=class_query)

    if emotion_query:
        dreams = dreams.filter(emotion=emotion_query)

    if keyword_query:
        dreams = dreams.filter(Q(keywords__iregex=r'\b{}\b'.format(re.escape(keyword_query))))

    if character_query:
        dreams = dreams.filter(characters__icontains=character_query)

    if place_query:
        dreams = dreams.filter(places__icontains=place_query)


    context = {
        'dreams': dreams,
        'query': query,
        'is_liked_view': False,
        'class_query': class_query,
        'keyword_query': keyword_query,
        'character_query': character_query,
        'place_query': place_query,
        'emotion_query': emotion_query,
    }
    return render(request, 'dreams/gallery.html', context)


@login_required
def like_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)

    DreamLike.objects.create(user=request.user, dream=dream)
    return redirect(request.META.get('HTTP_REFERER', 'dreams:gallery'))

@login_required
def unlike_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)

    existing_like = DreamLike.objects.filter(user=request.user, dream=dream).first()

    if existing_like:
        existing_like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'dreams:gallery'))



@login_required
def dream_journal(request):
    query = request.GET.get('q', '')
    class_query = request.GET.get('classification', '')
    emotion_query = request.GET.get('emotion', '')
    character_query = request.GET.get('character', '')
    place_query = request.GET.get('place', '')
    dreams = Dream.objects.filter(user=request.user)
    keyword_query = request.GET.get('keyword', '')

        # if query:
        #     dreams = dreams.filter(content__icontains=query) - > for substring
    # find also plural forms and possesive forms

    if query:
        regex_pattern = r'\b({}|{}s?|{}\'s?)\b'.format(re.escape(query), re.escape(query), re.escape(query))
        dreams = dreams.filter(Q(content__iregex=regex_pattern))

    if class_query:
        dreams = dreams.filter(classification=class_query)

    if emotion_query:
        dreams = dreams.filter(emotion=emotion_query)

    if keyword_query:
        regex_pattern = r'\b({}|{}s?|{}\'s?)\b'.format(re.escape(keyword_query), re.escape(keyword_query), re.escape(keyword_query))
        dreams = dreams.filter(Q(content__iregex=regex_pattern))

    if character_query:
        regex_pattern = r'\b({}|{}s?|{}\'s?)\b'.format(re.escape(character_query), re.escape(character_query), re.escape(character_query))
        dreams = dreams.filter(Q(content__iregex=regex_pattern))

    if place_query:
        dreams = dreams.filter(places__icontains=place_query)
    dreams = dreams.order_by('-date', '-time')

    context = {
        'dreams': dreams,
        'query': query,
        'class_query': class_query,
        'emotion_query': emotion_query,
        'keyword_query': keyword_query,
        'character_query': character_query,
        'place_query': place_query
    }
    return render(request, 'dreams/dream_journal.html', context)


@login_required
def view_favorite(request):
    query = request.GET.get('q', '')
    dreams = Dream.objects.filter(is_favorite=True, user=request.user)

    if query:
        dreams = dreams.filter(content__icontains=query)
    dreams = dreams.order_by('-date', '-time')
    context = {
        'dreams': dreams,
        'query': query,
        'is_favorite_view': True,
    }
    return render(request, 'dreams/dream_journal.html', context)

@login_required
def view_shared(request):
    query = request.GET.get('q', '')
    dreams = Dream.objects.filter(shared=True)

    if query:
        dreams = dreams.filter(content__icontains=query)

    dreams = dreams.order_by('-date', '-time')

    context = {
        'dreams': dreams,
        'query': query,
        'is_shared_view': True,
    }
    return render(request, 'dreams/dream_journal.html', context)


@login_required
def view_own_shared(request):
    query = request.GET.get('q', '')
    dreams = Dream.objects.filter(user=request.user, shared=True)

    if query:
        dreams = dreams.filter(content__icontains=query)

    dreams = dreams.order_by('-date', '-time')

    context = {
        'dreams': dreams,
        'query': query,
        'is_shared_view': True,
    }
    return render(request, 'dreams/dream_journal.html', context)


@login_required
def view_liked(request):
    query = request.GET.get('q', '')

    liked_dream_likes = DreamLike.objects.filter(user=request.user)
    liked_dreams = [dream_like.dream for dream_like in liked_dream_likes]
    for dream in liked_dreams:
        dream.is_liked_by_user = True
        dream.likes_count = dream.likes_count
        dream.liked_users = dream.liked_users()

    if query:
        liked_dreams = [dream for dream in liked_dreams if query.lower() in dream.content.lower()]

    context = {
        'dreams': liked_dreams,
        'query': query,
        'is_liked_view': True,
    }
    return render(request, 'dreams/gallery.html', context)


@login_required
def personal_statistics(request):
    dreams = Dream.objects.filter(user=request.user)

    # get number of dreams
    dream_count = dreams.count()

    # get number of liked dreams
    liked_count = DreamLike.objects.filter(user=request.user).count()

    # get number of shared dreams
    shared_count = Dream.objects.filter(shared=True, user=request.user).count()

    # get number of favorite dreams
    favorite_count = Dream.objects.filter(is_favorite=True, user=request.user).count()

    # get overview of (own) classification of dreams
    if dream_count > 0:
        nightmare_count = round(dreams.filter(classification='0').count()/dream_count * 100)
        mundane_count = round(dreams.filter(classification='1').count()/dream_count * 100)
        lucid_count = round(dreams.filter(classification='2').count()/dream_count * 100)
        existential_count = round(dreams.filter(classification='3').count()/dream_count * 100)
        none_count = 100-nightmare_count-mundane_count-lucid_count-existential_count

    else:
        nightmare_count = 0
        mundane_count = 0
        lucid_count = 0
        existential_count = 0
        none_count = 0


    # keywords
    all_keywords = []
    for dream in dreams:
        all_keywords.extend(dream.keywords)

    keywords_counted = Counter(all_keywords)

    top_10_keywords = keywords_counted.most_common(10)

    # get overview of emotions of dreams
    if dream_count > 0:
        anger_count = round(dreams.filter(emotion='Anger').count() / dream_count * 100)
        apprehension_count = round(dreams.filter(emotion='Apprehension').count() / dream_count * 100)
        sadness_count = round(dreams.filter(emotion='Sadness').count() / dream_count * 100)
        confusion_count = round(dreams.filter(emotion='Confusion').count() / dream_count * 100)
        happiness_count = round(dreams.filter(emotion='Happiness').count() / dream_count * 100)
        none_emotion_count = 100-anger_count-apprehension_count-sadness_count-confusion_count-happiness_count

    else:
        anger_count = 0
        apprehension_count = 0
        sadness_count = 0
        confusion_count = 0
        happiness_count = 0
        none_emotion_count = 0

    # characters
    all_characters = []
    for dream in dreams:
        all_characters.extend(dream.characters)

    normalized_characters = [character.lower() for character in all_characters]
    characters_counted = Counter(normalized_characters)

    characters_counted = dict(Counter(normalized_characters))

    top_10_characters = dict(Counter(characters_counted).most_common(10))

    labels = list(top_10_characters.keys())
    counts = list(top_10_characters.values())

    # Plotting with Matplotlib
    plt.figure(figsize=(6, 3))
    plt.gca().set_facecolor('#f0f0f0')
    plt.bar(labels, counts, color='skyblue')

    plt.xticks(rotation=45)
    plt.tick_params(axis='both', which='major', labelsize=10, labelcolor='black')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save plot to a bytes buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    # places
    all_places = []
    for dream in dreams:
        all_places.extend(dream.places)

    places_counted = Counter(all_places)

    top_10_places = places_counted.most_common(10)

    context = {
        'dreams': dreams,
        'dream_count': dream_count,
        'liked_count': liked_count,
        'nightmare_count': nightmare_count,
        'mundane_count': mundane_count,
        'lucid_count': lucid_count,
        'existential_count': existential_count,
        'none_count': none_count,
        'shared_count': shared_count,
        'favorite_count': favorite_count,
        'top_10_keywords': top_10_keywords,
        'top_10_characters': top_10_characters,
        'top_10_places': top_10_places,
        'anger_count': anger_count,
        'apprehension_count': apprehension_count,
        'sadness_count': sadness_count,
        'plot_data': plot_data,
        'confusion_count': confusion_count,
        'happiness_count': happiness_count,
        'none_emotion_count': none_emotion_count,
    }

    return render(request, 'dreams/personal_statistics.html', context)

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


@login_required
def add_comment(request, dream_id):
    dream = get_object_or_404(Dream, pk=dream_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.dream = dream
            comment.author = request.user
            comment.save()
            return redirect('dreams:gallery')
    else:
        form = CommentForm()

    comments = dream.comments.all()

    context = {
        'form': form,
        'dream': dream,
        'comments': comments,
    }
    return render(request, 'dreams/gallery.html', context)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.can_delete(request.user):
        comment.delete()
    else:
        return HttpResponseForbidden("You do not have permission to delete this comment.")
    return redirect('dreams:gallery')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
