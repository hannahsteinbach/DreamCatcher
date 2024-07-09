from django.urls import path
from . import views

app_name = 'dreams'

urlpatterns = [
    path('', views.home, name='home'),
    path('home_logged_in/', views.home_logged_in, name='home_logged_in'),
    path('log_dream/', views.log_dream, name='log_dream'),
    path('choose_title/<int:dream_id>/', views.choose_title, name='choose_title'),
    path('journal/', views.dream_journal, name='dream_journal'),
    path('edit_dream/<int:dream_id>/', views.edit_dream, name='edit_dream'),
    path('add_to_favorites/<int:dream_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:dream_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('share_dream/<int:dream_id>/', views.share_dream, name='share_dream'),
    path('share_dream_anon/<int:dream_id>/', views.share_dream_anon, name='share_dream_anon'),
    path('unshare_dream/<int:dream_id>/', views.unshare_dream, name='unshare_dream'),
    path('delete_dream/<int:dream_id>/', views.delete_dream, name='delete_dream'),
    path('like_dream/<int:dream_id>/', views.like_dream, name='like_dream'),
    path('unlike_dream/<int:dream_id>/', views.unlike_dream, name='unlike_dream'),
    path('view_favorite/', views.view_favorite, name='view_favorite'),
    path('view_shared/', views.view_shared, name='view_shared'),
    path('view_own_shared/', views.view_own_shared, name='view_own_shared'),
    path('view_liked', views.view_liked, name='view_liked'),
    path('add_comment/<int:dream_id>/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('statistics/', views.personal_statistics, name='personal_statistics'),
    path('gallery/', views.gallery, name='gallery'),
]
