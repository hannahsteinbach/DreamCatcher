from django.urls import path
from . import views

app_name = 'dreams'

urlpatterns = [
    path('', views.home, name='home'),
    path('log/', views.log_dream, name='log_dream'),
    path('journal/', views.dream_journal, name='dream_journal'),
    path('statistics/', views.personal_statistics, name='personal_statistics'),
    path('questionnaires/', views.questionnaires, name='questionnaires'),
]
