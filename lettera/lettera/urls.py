from lettera import views
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^contact/$', views.AboutView.as_view(), name='about'),
    url(r'^about/$', views.ContactView.as_view(), name='contact'),
    url(r'^browser/', include('browser.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
