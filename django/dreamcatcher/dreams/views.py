from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'dreams/home.html')

def log_dream(request):
    return render(request, 'dreams/log_dream.html')

def questionnaires(request):
    return render(request, 'dreams/questionnaires.html')

def dream_journal(request):
    return render(request, 'dreams/dream_journal.html')

def personal_statistics(request):
    return render(request, 'dreams/personal_statistics.html')
