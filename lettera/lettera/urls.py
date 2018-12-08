from lettera import views
from django.urls import include, re_path, path
from django.contrib.auth.views import LoginView, LogoutView

from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = [
    path(
        'accounts/login/',
        LoginView.as_view(template_name='registration/login.html'),
        name='login'),
    path(
        'accounts/logout/',
        LogoutView.as_view(template_name='registration/logged_out.html'),
        name='logout'),
    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.AboutView.as_view(), name='about'),
    path('about/', views.ContactView.as_view(), name='contact'),
    path('browser/', include('browser.urls')),
    path('admin/', admin.site.urls)
]
