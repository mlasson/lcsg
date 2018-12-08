from django.urls import include, re_path
from browser import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(
        r'^hypertest/$', views.HypertestView.as_view(),
        name='index-hypertest'),
    re_path(
        r'^ajax/hypertest-histo/$',
        views.hypertest_histogram,
        name='ajax-hypertest-histogram'),
    re_path(
        r'^ajax/subcorpus-search/$',
        views.search_subcorpus,
        name='ajax-subcorpus-search'),
    re_path(
        r'^ajax/subcorpus-create/$',
        views.create_subcorpus,
        name='ajax-subcorpus-create'),
    re_path(
        r'^ajax/subcorpus-delete/$',
        views.delete_subcorpus,
        name='ajax-subcorpus-delete'),
    re_path(
        r'^ajax/subcorpus-list/$',
        views.get_subcorpi,
        name='ajax-subcorpus-list'),
    re_path(
        r'^ajax/index-families/$',
        views.index_families_post,
        name='ajax-index-families'),
    re_path(
        r'^index-families/$',
        views.FamiliesView.as_view(),
        name='index-families'),
    re_path(
        r'^ajax/letter-from-date/(?P<start>\d\d\d\d-\d\d-\d\d)/(?P<end>\d\d\d\d-\d\d-\d\d)/$',
        views.letters_from_date,
        name='ajax-letters-from-date'),
    re_path(
        r'^ajax/index/(?P<letters>(\d+,)*\d+)/$',
        views.index_letter,
        name='index-ajax-letters-subcorpus-list'),
    re_path(
        r'^ajax/index/(?P<subcorpus>[a-zA-Z]+)/$',
        views.index_letter_subcorpus,
        name='index-ajax-letters-subcorpus'),
    re_path(r'^ajax/index/$', views.index_letter, name='index-ajax'),
    re_path(
        r'^ajax/create/subcorpus/(?P<ident>[a-zA-Z]+)/(?P<letters>(\d+,)*\d+)/',
        views.create_subcorpus_full,
        name='create-subcorpus'),
    re_path(r'^quote/$', views.QuoteView.as_view(), name='quote'),
    re_path(r'^ajax/quote/$', views.index_quote, name='quote-ajax'),
    re_path(r'^word/$', views.WordView.as_view(), name='index-word'),
    re_path(r'^ajax/word/$', views.index_word, name='index-word-ajax'),
    re_path(r'^period/$', views.PeriodView.as_view(), name='index-period'),
    re_path(r'^ajax/period/$', views.index_period, name='index-period-ajax'),
    re_path(r'^francia/$', views.FranciaView.as_view(), name='index-francia'),
    re_path(
        r'^ajax/francia/$', views.index_francia, name='index-francia-ajax'),
    re_path(
        r'^ajax/occurrences/(?P<pks>([\d]+,)*\d+)/$',
        views.occurrences_index,
        name='occurrences-get-ajax'),
    re_path(r'^ajax/participe/$', views.participe, name='participe-ajax'),
    re_path(
        r'^ajax/occurrence-word/(?P<pk>\d+)/$',
        views.occurrence_word,
        name='occurrence-word-ajax'),
    re_path(
        r'^ajax/forward-tree/(?P<pk>\d+)/$',
        views.word_forward_tree,
        name='occurrence-forward-tree-ajax'),
    re_path(
        r'^ajax/backward-tree/(?P<pk>\d+)/$',
        views.word_backward_tree,
        name='occurrence-backward-tree-ajax'),
    re_path(
        r'^ajax/family-forward-tree/(?P<pk>\d+)/$',
        views.family_forward_tree,
        name='family-forward-tree-ajax'),
    re_path(
        r'^ajax/family-backward-tree/(?P<pk>\d+)/$',
        views.family_backward_tree,
        name='family-backward-tree-ajax'),
    re_path(
        r'^occurrence-word/(?P<pk>\d+)/$',
        views.OccurrenceWordView.as_view(),
        name='occurrence-word'),
    re_path(
        r'^ajax/occurrence-family/(?P<pk>\d+)/$',
        views.occurrence_family,
        name='occurrence-family-ajax'),
    re_path(
        r'^occurrence-family/(?P<pk>\d+)/$',
        views.OccurrenceFamilyView.as_view(),
        name='occurrence-family'),
    re_path(r'^participe/$', views.ParticipeView.as_view(), name='participe'),
    re_path(
        r'^ajax/participe-backward-tree/$',
        views.participe_backward_tree,
        name='participe-backward-tree-ajax'),
    re_path(
        r'^ajax/participe-forward-tree/$',
        views.participe_forward_tree,
        name='participe-forward-tree-ajax'),
    re_path(
        r'^ajax/occurrences/$',
        views.occurrences_index,
        name='occurrences-post-ajax'),
    re_path(
        r'^ajax/sentence/(?P<pk>\d+)/$', views.sentence, name='sentence-ajax'),
    re_path(
        r'^ajax/occurrences-letter/(?P<pk>\d+)/$',
        views.occurrences_letter,
        name='occurrences-ajax'),
    re_path(
        r'^(?P<pagesize>\d+)/(?P<page>\d+)/$',
        views.IndexView.as_view(),
        name='index-with-page'),
    re_path(r'^(?P<pk>\d+)/', views.LetterView.as_view(), name='letter'),
    re_path(
        r'^modal/(?P<pk>\d+)/',
        views.ModalLetterView.as_view(),
        name='modal-letter'),
    re_path(r'^zipf/', views.ZipfView.as_view(), name='zipflaw')
]
