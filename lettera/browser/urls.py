from django.conf.urls import url
from browser import views

urlpatterns = [
        url(r'^$', views.IndexView.as_view(), name='index'), 
        url(r'^ajax/index/$', views.index_letter, name='index-ajax'), 
        url(r'^quote/$', views.QuoteView.as_view(), name='quote'), 
        url(r'^ajax/quote/$', views.index_quote, name='quote-ajax'), 
        url(r'^word/$', views.WordView.as_view(), name='index-word'), 
        url(r'^ajax/word/$', views.index_word, name='index-word-ajax'), 
        url(r'^family/$', views.FamilyView.as_view(), name='index-family'), 
        url(r'^ajax/family/$', views.index_family, name='index-family-ajax'), 
        url(r'^period/$', views.PeriodView.as_view(), name='index-period'), 
        url(r'^ajax/period/$', views.index_period, name='index-period-ajax'), 
        url(r'^francia/$', views.FranciaView.as_view(), name='index-francia'), 
        url(r'^ajax/francia/$', views.index_francia, name='index-francia-ajax'), 
        url(r'^ajax/occurrences/(?P<pks>([\d]+,)*\d+)/$', views.occurrences_index, name='occurrences-get-ajax'), 
        url(r'^ajax/participe/$', views.participe, name='participe-ajax'), 
        url(r'^ajax/all-occurrences/(?P<pk>\d+)/$', views.all_occurrences, name='occurrence-word-ajax'), 
        url(r'^all-occurrences/(?P<pk>\d+)/$', views.OccurrenceWordView.as_view(), name='occurrence-word'), 
        url(r'^participe/$', views.ParticipeView.as_view(), name='participe'), 
        url(r'^ajax/occurrences/$', views.occurrences_index, name='occurrences-post-ajax'), 
        url(r'^ajax/sentence/(?P<pk>\d+)/$', views.sentence, name='sentence-ajax'), 
        url(r'^ajax/occurrences-letter/(?P<pk>\d+)/$', views.occurrences_letter, name='occurrences-ajax'), 
        url(r'^(?P<pagesize>\d+)/(?P<page>\d+)/$', views.IndexView.as_view(), name='index-with-page'), 
        url(r'^(?P<pk>\d+)/', views.LetterView.as_view(), name='letter'),
        url(r'^modal/(?P<pk>\d+)/', views.ModalLetterView.as_view(), name='modal-letter'),
  ]
