from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.utils.timezone import now
from datetime import timedelta, datetime
from .forms import CustomPasswordResetForm
from django.core.paginator import Paginator
from django.views.generic.detail import DetailView
from django.http import HttpResponseForbidden
from .forms import SignUpForm, DreamForm, CommentForm, DateForm, UpdateProfileForm, UpdateUserForm, QuestionnaireForm
import logging
from django.shortcuts import render, redirect
from .models import Dream, DreamLike, Comment, User, MonthlyRecap
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.db.models import F
from django.db.models import Q
from django.shortcuts import get_object_or_404
from collections import Counter
import re
from django.db.models import Count
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import json
from .utils import find_similar_dreams, add_dream_to_collection, remove_dream_from_collection, get_dream_by_id, update_dream_shared_status_in_collection
from django.urls import reverse
from langchain_community.llms import ollama
from urllib.parse import unquote
from django.shortcuts import render


logger = logging.getLogger(__name__)


def home(request):
    if request.user.is_authenticated:
        return redirect('dreams:home_logged_in')
    return render(request, 'base_generic.html')


def aboutus(request):
    return render(request, 'aboutus.html')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='dreams:dream_journal')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'dreams/profile.html', {'user_form': user_form, 'profile_form': profile_form})



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

        add_dream_to_collection(dream.id, dream.content)

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
                return redirect('dreams:choose_title_log', dream_id=dream.id)
        #else:
         #   messages.error(request, "Failed to log your dream. Please correct the errors below.")

    else:
        form = DateForm(initial={'date': date.today()})

    return render(request, 'dreams/log_dream.html', {'form': form})


@login_required
def view_similar_own(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    user = request.user

    user_dreams = Dream.objects.filter(user=user)
    dream_count = user_dreams.count()
    n_results = min(6, dream_count)  # Check how many dreams user has, return at most 6

    dreams_scores = find_similar_dreams(dream, user, user_specific=True, n_results=n_results)
    # llama_dreams = []

    # for dream, scores in dreams_scores:
    #     llama_dreams.append(dream.content)

    # llm = ollama.Ollama(model='llama3', temperature=0, top_p=1, verbose=False)

    # similarity_prompt = (
    #     f"Here is an original dream:\n{llama_dreams[0]}\n\n"
    #     f"Below is a list of dreams similar to the original dream:\n"
    #     f"{llama_dreams[1:]}\n\n"
    #     "For each similar dream, write a explanation of how it is similar to or different from the original dream. "
    #     "Format the output as a list of strings where each string corresponds to one of the similar dreams. "
    #     "The list should be formatted in Python syntax (e.g., ['Comparison 1', 'Comparison 2']). "
    #     "Do not include any additional information or assumptions."
    # )

    # try:
    #     # response generation
    #     response = llm.invoke(similarity_prompt)
    #     print("Raw response:", response)
    #     response = json.loads(response)
    #     print("JSON response:", response)

    # except (json.JSONDecodeError, KeyError) as e:
    #     print(f"Error processing similarity explanation: {e}")

    # dreams_scores_explanation = [
    #     (dream, score, explanation) for (dream, score), explanation in zip(dreams_scores, response)
    # ]

    # print(dreams_scores_explanation)


    context = {
        'dreams_scores': dreams_scores,
        'query': request.GET.get('query', ''),
        'user': user
    }
    return render(request, 'dreams/view_similar_own.html', context)


@login_required()
def view_similar_all(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    user = request.user

    dreams_scores = find_similar_dreams(dream, user, user_specific=False)

    context = {
        'dreams_scores': dreams_scores,
        'query': request.GET.get('query', ''),
        'user': user
    }
    return render(request, 'dreams/view_similar_all.html', context)

@login_required
def choose_title_log(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    optional_titles = dream.optional_titles
    if not optional_titles:
        remove_dream_from_collection(dream_id)
        dream.delete()
    else:
        if request.method == 'POST':
            selected_title = request.POST.get('title')
            if selected_title:
                dream.title = selected_title
                dream.save()
                if not dream.emotion:
                    return redirect('dreams:choose_emotion', dream_id=dream.id)
                else:
                    return redirect('dreams:questionnaire_log', dream_id=dream.id)
    return render(request, 'dreams/choose_title_log.html', {'dream': dream})


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
                return redirect('dreams:dream_journal')
          #  else:
           #     messages.error(request, 'Please select a title.')
    return render(request, 'dreams/choose_title.html', {'dream': dream})


@login_required
def regenerate_titles(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    dream.generate_titles()  # Call the title regeneration function
    dream.save()  # Save the updated titles
    return redirect('dreams:choose_title_log', dream_id=dream.id)

@login_required
def choose_emotion(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    if request.method == 'POST':
        selected_emotion = request.POST.get('emotion')
        dream.emotion = selected_emotion
        dream.save()
        return redirect('dreams:questionnaire_log', dream_id=dream.id)
    return render(request, 'dreams/choose_emotion.html', {'dream': dream})


@login_required
def questionnaire_log(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)

    if hasattr(dream, 'questionnaire'):
        questionnaire = dream.questionnaire
        form = QuestionnaireForm(instance=questionnaire)

    else:
        questionnaire = None
        form = QuestionnaireForm()


    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            if questionnaire is None:
                questionnaire = form.save(commit=False)
                questionnaire.dream = dream
                questionnaire.save()
            else:
                form.save()
            return redirect('dreams:dream_journal')

    return render(request, 'dreams/questionnaire_log.html', {'form': form, 'dream': dream})


@login_required
def questionnaire(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id)
    edit_questionnaire = False
    view_only = request.method == 'GET'

    if hasattr(dream, 'questionnaire'):
        questionnaire = dream.questionnaire
        form = QuestionnaireForm(instance=questionnaire)

        # read only (for viewing questionnaire)
        if view_only:
            for field in form.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

    else:
        questionnaire = None
        form = QuestionnaireForm()


    if request.method == 'POST':
        if 'edit_questionnaire' in request.POST:
            edit_questionnaire = True
            view_only = False
            form = QuestionnaireForm(instance=questionnaire)
            return render(request, 'dreams/questionnaire.html', {'form': form, 'dream': dream, 'view_only': view_only, 'edit_questionnaire': edit_questionnaire})

        form = QuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            if questionnaire is None:
                questionnaire = form.save(commit=False)
                questionnaire.dream = dream
                questionnaire.save()
            else:
                form.save()
            return redirect('dreams:dream_journal')

    return render(request, 'dreams/questionnaire.html', {'form': form, 'dream': dream, 'view_only': view_only, 'edit_questionnaire': edit_questionnaire})


@login_required
def delete_dream(request, dream_id):
    dream_embedding = get_dream_by_id(dream_id)
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    if dream_embedding:
        remove_dream_from_collection(dream_id)
        messages.success(request, "Dream deleted successfully.")
    else:
        messages.error(request, "Dream does not exist.")
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
                    remove_dream_from_collection(dream.id) #just try this again (delulu queen), if it doesnt work change back
                    add_dream_to_collection(dream.id, dream.content)
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
    #messages.success(request, 'Dream was successfully added to favorites!')
    # all messages dont work
    return redirect(request.META.get('HTTP_REFERER', 'dreams:dream_journal'))


@login_required
def remove_from_favorites(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.is_favorite = False
    dream.save(update_fields=['is_favorite'])
    #messages.success(request, 'Dream was successfully removed from favorites!')
    return redirect(request.META.get('HTTP_REFERER', 'dreams:dream_journal'))

@login_required
def share_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.shared = True
    dream.anon = False
    dream.save(update_fields=['shared'])
    dream.save(update_fields=['anon'])
    update_dream_shared_status_in_collection(dream.id, shared=True)


   # messages.success(request, 'Dream shared successfully!')
    return redirect('dreams:dream_journal')

@login_required
def share_dream_anon(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.shared = True
    dream.anon = True
    dream.save(update_fields=['shared'])
    dream.save(update_fields=['anon'])
    update_dream_shared_status_in_collection(dream.id, shared=True)
  #  messages.success(request, 'Dream shared successfully!')
    return redirect('dreams:dream_journal')


def view_users_dreams(request, username):
    user = get_object_or_404(User, username=username)
    query = request.GET.get('q', '')
    dreams = Dream.objects.filter(shared=True, user=user, anon=False)
    class_query = request.GET.get('classification', '')
    emotion_query = request.GET.get('emotion', '')
    keyword_query = request.GET.get('keyword', '')
    character_query = request.GET.get('character', '')
    place_query = request.GET.get('place', '')

    if query:
        regex_pattern = r'\b({}|{}s?|{}\'s?)\b'.format(re.escape(query), re.escape(query),
                                                       re.escape(query))
        dreams = dreams.filter(Q(content__iregex=regex_pattern))

    if class_query:
        dreams = dreams.filter(classification=class_query)

    if emotion_query:
        dreams = dreams.filter(emotion=emotion_query)

    if keyword_query:
        dreams = dreams.filter(Q(keywords__iregex=r'\b{}\b'.format(re.escape(keyword_query))))

    if character_query:
        dreams = dreams.filter(Q(characters__iregex=r'\b{}\b'.format(re.escape(character_query))))

    if place_query:
        dreams = dreams.filter(Q(places__iregex=r'\b{}\b'.format(re.escape(place_query))))

    dreams = dreams.order_by('-date', '-time')

    paginator = Paginator(dreams, 10)  # Show 10 dreams per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'dreams': page_obj,
        'user': user,
        'query': query,
        'class_query': class_query,
        'keyword_query': keyword_query,
        'character_query': character_query,
        'place_query': place_query,
        'emotion_query': emotion_query,
    }
    return render(request, 'dreams/view_user.html', context)


@login_required
def unshare_dream(request, dream_id):
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    dream.shared = False
    dream.save(update_fields=['shared'])
    update_dream_shared_status_in_collection(dream.id, shared=False)

    DreamLike.objects.filter(dream=dream).delete() # remove all likes associated with dream

    Comment.objects.filter(dream=dream).delete() # remove all comments associated with deram
    return redirect('dreams:dream_journal')


@login_required
def gallery(request):
    query = request.GET.get('q', '')
    query_user = request.GET.get('qu', '')
    user_found = True
    dreams = Dream.objects.filter(shared=True)
    class_query = request.GET.get('classification', '')
    emotion_query = request.GET.get('emotion', '')
    keyword_query = request.GET.get('keyword', '')
    character_query = request.GET.get('character', '')
    place_query = request.GET.get('place', '')


    if query_user:
        user = User.objects.filter(username=query_user).first()
        if user:
            return redirect('dreams:view_users_dreams', username=query_user)
        else:
            user_found = False

    if query:
        regex_pattern = r'\b({}|{}s?|{}\'s?)\b'.format(re.escape(query), re.escape(query),
                                                       re.escape(query))
        dreams = dreams.filter(Q(content__iregex=regex_pattern))

    if class_query:
        dreams = dreams.filter(classification=class_query)

    if emotion_query:
        dreams = dreams.filter(emotion=emotion_query)

    if keyword_query:
        dreams = dreams.filter(Q(keywords__iregex=r'\b{}\b'.format(re.escape(keyword_query))))

    if character_query:
        dreams = dreams.filter(Q(characters__iregex=r'\b{}\b'.format(re.escape(character_query))))

    if place_query:
        dreams = dreams.filter(Q(places__iregex=r'\b{}\b'.format(re.escape(place_query))))

    dreams = dreams.order_by('-date', '-time')

    for dream in dreams:
        dream.is_liked_by_user = DreamLike.objects.filter(user=request.user, dream=dream).exists()

    paginator = Paginator(dreams, 10)  # Show 10 dreams per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'dreams': page_obj,
        'query': query,
        'is_liked_view': False,
        'class_query': class_query,
        'keyword_query': keyword_query,
        'character_query': character_query,
        'place_query': place_query,
        'emotion_query': emotion_query,
        'query_user': query_user,
        'user_found': user_found,
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
    place_query = unquote(place_query)
    dreams = Dream.objects.filter(user=request.user)
    keyword_query = request.GET.get('keyword', '')

        # if query:
        #     dreams = dreams.filter(content__icontains=query) - > for substring
    # find also plural forms and possesive forms

    if query:
        regex_pattern = r'\b({}|{}s?|{}\'s?)\b'.format(re.escape(query), re.escape(query),
                                                       re.escape(query))
        dreams = dreams.filter(Q(content__iregex=regex_pattern))

    if class_query:
        dreams = dreams.filter(classification=class_query)

    if emotion_query:
        dreams = dreams.filter(emotion=emotion_query)

    if keyword_query:
        dreams = dreams.filter(Q(keywords__iregex=r'\b{}\b'.format(re.escape(keyword_query))))

    if character_query:
        dreams = dreams.filter(Q(characters__iregex=r'\b{}\b'.format(re.escape(character_query))))

    if place_query:
        dreams = dreams.filter(Q(places__iregex=r'\b{}\b'.format(re.escape(place_query))))

    dreams = dreams.order_by('-date', '-time')

    paginator = Paginator(dreams, 10)  # Show 10 dreams per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(f"Decoded place: {place_query}")


    context = {
        'dreams': page_obj,
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

    dream_types = [
            {'name': 'Nightmares', 'count': nightmare_count},
            {'name': 'Mundane dreams', 'count': mundane_count},
            {'name': 'Lucid dreams', 'count': lucid_count},
            {'name': 'Existential dreams', 'count': existential_count},
            {'name': 'Not classified', 'count': none_count},
        ]

    dream_types_sorted = sorted(dream_types, key=lambda x: x['count'], reverse=True)

    # keywords
    all_keywords = []
    for dream in dreams:
        all_keywords.extend(dream.keywords)

    keywords_counted = Counter(all_keywords)

    top_10_keywords = keywords_counted.most_common(10)

    # get overview of emotions of dreams
    if dream_count > 0:
        anger_count = round(dreams.filter(emotion='anger').count() / dream_count * 100)
        apprehension_count = round(dreams.filter(emotion='apprehension').count() / dream_count * 100)
        sadness_count = round(dreams.filter(emotion='sadness').count() / dream_count * 100)
        confusion_count = round(dreams.filter(emotion='confusion').count() / dream_count * 100)
        happiness_count = round(dreams.filter(emotion='happiness').count() / dream_count * 100)
        none_emotion_count = 100-anger_count-apprehension_count-sadness_count-confusion_count-happiness_count

    else:
        anger_count = 0
        apprehension_count = 0
        sadness_count = 0
        confusion_count = 0
        happiness_count = 0
        none_emotion_count = 0

    emotions = [
        {'name': 'Anger', 'count': anger_count},
        {'name': 'Apprehension', 'count': apprehension_count},
        {'name': 'Sadness', 'count': sadness_count},
        {'name': 'Confusion', 'count': confusion_count},
        {'name': 'Happiness', 'count': happiness_count},
        {'name': 'Neutral', 'count': none_emotion_count},
    ]

    emotions_sorted = sorted(emotions, key=lambda x: x['count'], reverse=True)

    all_characters = []
    for dream in dreams:
        all_characters.extend(dream.characters)

    character_counts = Counter()
    for char in set(all_characters):
        count = dreams.filter(Q(characters__iregex=r'(?i)\b{}\b'.format(re.escape(char)))).count()
        character_counts[char] = count

    top_10_characters = dict(character_counts.most_common(10))


    labels = list(top_10_characters.keys())
    character_counts = list(top_10_characters.values())

    dream_dates = [dream.date for dream in dreams]
    dream_dates_counted = Counter(dream_dates)

    dates = [date.strftime('%Y-%m-%d') for date in dream_dates_counted.keys()]
    dream_counts = list(dream_dates_counted.values())

    dates_json = json.dumps(dates)
    dream_counts_json = json.dumps(dream_counts)

    current_month = datetime.now().date().replace(day=1)
    
    first_dream = dreams.order_by('date').first()
    if first_dream:
        first_month = first_dream.date.replace(day=1)
    else:
        first_month = current_month  

    available_months = []
    while current_month >= first_month:
        available_months.append(current_month)
        current_month = (current_month - timedelta(days=1)).replace(day=1)

    available_months = [current_month - timedelta(days=30 * i) for i in range((current_month - first_month).days // 30 + 1)]

    # plot 2: top characters
    plt.figure(figsize=(6, 3))
    plt.gca().set_facecolor('#f0f0f0')
    plt.bar(labels, character_counts, color='skyblue')

    plt.xticks(rotation=45)
    plt.tick_params(axis='both', which='major', labelsize=10, labelcolor='black')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png', transparent=True)
    buffer2.seek(0)
    plot_data2 = base64.b64encode(buffer2.getvalue()).decode()
    buffer2.close()

    all_places = []
    for dream in dreams:
        all_places.extend(dream.places)

    place_counts = Counter()
    for place in set(all_places):
        count = dreams.filter(Q(places__iregex=r'(?i)\b{}\b'.format(re.escape(place)))).count()
        place_counts[place] = count

    top_10_places = place_counts.most_common(10)

    ### MONTHLY RECAP
    current_month = now().date().replace(day=1)
    desired_month = None

    if request.method == 'POST':
        desired_month_user = request.POST.get('desired_month')

        if desired_month_user:
            year, month = map(int, desired_month_user.split('-'))
            desired_month = date(year, month, 1)

            recap, _ = MonthlyRecap.objects.get_or_create(user=request.user, month=desired_month)
            recap.generate_recap()
            recap.save()

            # check for nightmares (for displaying)
            nightmares = True
            dreams_in_month = dreams.filter(date__year=year, date__month=month)
            if not dreams_in_month.filter(classification='0').exists():
                nightmares = False
            context = {
                'recap': recap,
                'desired_month': desired_month.strftime('%B %Y') if desired_month else None,
                'nightmares': nightmares
            }
            return render(request, 'dreams/view_recap.html', context)

    first_dream = Dream.objects.filter(user=request.user).order_by('date').first()  # get first dream to get first month
    first_month = first_dream.date.replace(day=1) if first_dream else current_month

    available_months = []
    while current_month >= first_month:
        available_months.append(current_month)
        current_month = (current_month - timedelta(days=1)).replace(day=1)

    context = {
        'dreams': dreams,
        'dream_count': dream_count,
        'liked_count': liked_count,
        'emotions': emotions_sorted,
        'dream_types': dream_types_sorted,
        'shared_count': shared_count,
        'favorite_count': favorite_count,
        'top_10_keywords': top_10_keywords,
        'top_10_characters': top_10_characters,
        'top_10_places': top_10_places,
        'anger_count': anger_count,
        'apprehension_count': apprehension_count,
        'sadness_count': sadness_count,
        'plot_data2': plot_data2,
        'confusion_count': confusion_count,
        'happiness_count': happiness_count,
        'none_emotion_count': none_emotion_count,
        'available_months': available_months,
        'desired_month': desired_month,
        'dates': dates_json,
        'dream_counts': dream_counts_json
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
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('dreams:home_logged_in')
        else:
            logger.error("Form errors: %s", form.errors)
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
    comment.delete()
    return redirect('dreams:gallery')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def check_user_information(self, form):
    email = form.cleaned_data.get('email')
    username = form.cleaned_data.get('username')

    users = User.objects.filter(email=email, username=username)

    if not users.exists():
        form.add_error(None, "No user found with that username and email combination.")
        return self.form_invalid(form)

    return super().check_user_information(form)


@login_required
def home_logged_in(request):
    user = request.user
    dreams = Dream.objects.filter(user=user)
    show_tutorial = user.is_new
    if show_tutorial:
        user.is_new = False
        user.save()
    
    dream_count = dreams.count()
    liked_count = DreamLike.objects.filter(user=user).count()
    shared_count = dreams.filter(shared=True).count()

    dream_dates = dreams.order_by('-date').values_list('date', flat=True)

    if not dreams:
        dream_streak = 0
        max_streak = 0
    else:
        dream_streak = 1
        max_streak = 1

    for i in range(1, len(dream_dates)):
        if (dream_dates[i-1] - dream_dates[i]).days == 1:
            dream_streak += 1
        elif (dream_dates[i-1] - dream_dates[i]).days == 0:
            dream_streak += 0
        else:
            break

    streaks = []
    streak = 1
    for i in range(1, len(dream_dates)):
        if (dream_dates[i-1] - dream_dates[i]).days == 1:
            streak += 1
        elif (dream_dates[i-1] - dream_dates[i]).days == 0:
            streak += 0
        else:
            streak = 1
        streaks.append(streak)
    if len(streaks) > 0:
        max_streak = max(streaks)
    else:
        max_streak = 0

    all_keywords = []
    for dream in dreams:
        all_keywords.extend(dream.keywords)
    
    word_count = Counter(all_keywords)
    word_cloud_data = [{"text": word, "size": count * 10} for word, count in word_count.most_common(20)]

    context = {
        'dream_count': dream_count,
        'liked_count': liked_count,
        'shared_count': shared_count,
        'dream_streak': dream_streak,
        'max_streak': max_streak,
        'word_cloud_data': json.dumps(word_cloud_data),
        'show_tutorial': show_tutorial,
        'log_dream_url': reverse('dreams:log_dream'),
        'dream_journal_url': reverse('dreams:dream_journal'),
        'gallery_url': reverse('dreams:gallery'),
        'personal_statistics_url': reverse('dreams:personal_statistics'),

    }
    
    return render(request, 'home.html', context)