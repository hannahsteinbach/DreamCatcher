from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from dreams import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dreams/', include('dreams.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
]
