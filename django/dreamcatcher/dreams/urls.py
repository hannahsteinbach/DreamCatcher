from django.urls import path
from . import views

app_name = 'dreams'

urlpatterns = [
    path('', views.home, name='home'),
    path('home_logged_in/', views.home_logged_in, name='home_logged_in'),
    path('log_dream/', views.log_dream, name='log_dream'),
    path('journal/', views.dream_journal, name='dream_journal'),
    path('delete_dream/<int:dream_id>/', views.delete_dream, name='delete_dream'),
    path('statistics/', views.personal_statistics, name='personal_statistics'),
    path('questionnaires/', views.questionnaires, name='questionnaires'),
]
