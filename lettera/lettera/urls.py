from lettera import views
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^contact/$', views.AboutView.as_view(), name='about'),
    url(r'^about/$', views.ContactView.as_view(), name='contact'),
    url(r'^browser/', include('browser.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
