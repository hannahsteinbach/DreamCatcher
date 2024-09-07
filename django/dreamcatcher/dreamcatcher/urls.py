from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from dreams.views import CustomPasswordResetView

from dreams import views

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

    # Dreams URLs
    path('dreams/', include('dreams.urls')),

    # User Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Custom URLs
    path('aboutus/', views.aboutus, name='aboutus'),
    path('', views.home, name='home'),

    # Password Reset URLs
    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

]
