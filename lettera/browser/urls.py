from django.conf.urls import url
from browser import views

urlpatterns = [
        url(r'^$', views.IndexView.as_view(), name='index'), 
        url(r'^index-ajax/$', views.index_letter, name='index-ajax'), 
        url(r'^word/$', views.WordView.as_view(), name='index-word'), 
        url(r'^word-ajax/$', views.index_word, name='index-word-ajax'), 
        url(r'^family/$', views.FamilyView.as_view(), name='index-family'), 
        url(r'^family-ajax/$', views.index_family, name='index-family-ajax'), 
        url(r'^period/$', views.PeriodView.as_view(), name='index-period'), 
        url(r'^period-ajax/$', views.index_period, name='index-period-ajax'), 
        url(r'^francia/$', views.FranciaView.as_view(), name='index-francia'), 
        url(r'^francia-ajax/$', views.index_francia, name='index-francia-ajax'), 
        url(r'^occurrences-ajax/(?P<pk>\d+)/$', views.index_occurrences, name='occurrences-ajax'), 
        url(r'^(?P<pagesize>\d+)/(?P<page>\d+)/$', views.IndexView.as_view(), name='index-with-page'), 
        url(r'^(?P<pk>\d+)/', views.LetterView.as_view(), name='letter'),
        url(r'^modal/(?P<pk>\d+)/', views.ModalLetterView.as_view(), name='modal-letter'),
  ]
