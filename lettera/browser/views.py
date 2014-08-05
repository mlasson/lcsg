import json
import math
from datetime import datetime, time
from collections import Counter, defaultdict
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.db.models import Count, Q, query
from django.shortcuts import render
from django.http import HttpResponse 
from django.views import generic
from browser.models import *
from django.core.paginator import Paginator
from utils.suffixtree import SuffixTree

class json_cache(object):
  def __init__(self, func):
    self.func = func
    self.name = func.__name__
    
  def __call__(self, arg, **args):
    query = Cache.objects.filter(name = self.name, args = repr(arg.path)).first()
    if not query:
      result = self.func(arg, **args)
      new_entry = Cache(name=self.name, args=repr(arg.path), value = result)
      new_entry.save()
    else :
      result = query.value
    return HttpResponse(result, content_type='application/javascript')

class json_nocache(object):
  def __init__(self, func):
    self.func = func
    self.name = func.__name__
    
  def __call__(self, arg, **args):
    result = self.func(arg, **args)
    return HttpResponse(result, content_type='application/javascript')


def date_handler(obj):
  if hasattr(obj, 'isoformat') : 
    return obj.isoformat()
  else :
    raise TypeError ('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))

@json_cache
def index_letter(request) : 
  objects = Letter.objects.annotate(length=Count('occurrence')).order_by('pk')
  answer = list()
  for l in objects :
    r = dict()
    r['link'] = reverse('letter', args=(l.pk,))
    r['modal'] = reverse('modal-letter', args=(l.pk,))
    r['volume'] = l.volume
    r['number'] = l.number
    r['length'] = l.length
    r['date'] = l.date
    if l.period : 
      r['period'] = l.period.name
    else : 
      r['period'] = ''

    answer.append(r)

  return json.dumps({ 'aaData' : answer }, default=date_handler)

@json_cache
def occurrences_letter(request, pk) : 
  objects = Occurrence.objects.filter(letter_id = pk).order_by('pk').select_related('family','word')
  answer = list()
  for o in objects :
    r = dict()
    r['word'] = o.word.name
    r['letter'] = o.letter_id
    r['start_position'] = o.start_position
    r['end_position'] = o.end_position
    r['family'] = o.family.name
    answer.append(r)

  return json.dumps({ 'aaData' : answer })

@json_cache
def sentence(request, pk):
  sentence = Sentence.objects.get(pk=pk)
  letter = sentence.letter
  phrase = letter.text[sentence.start_position:sentence.end_position]
  return json.dumps(phrase)

def ellipse(front, word, back, maxsize=100):
  size = len(front)+len(word)+len(back)
  half = int((maxsize - len(word)) / 2) 
  diff = size - maxsize
  if diff > 0: 
    if len(front) < half :
      back = back[0:maxsize + len(back) - size]+u' …'
    elif len(back) < half :
      front =u'… '+front[-maxsize - len(front) + size:]
    else :
      back = back[:half]+u' …'
      front = u'… '+front[-half:]
  return (front,word,back)

def build_occurrence_table(occs) : 
  answer = list()
  occs = occs.select_related('word','sentence','letter', 'period')
  for o in occs:
    r = dict()
    r['link'] = (reverse('modal-letter', args=(o.letter_id,)),o.start_position,o.end_position)
    r['volume'] = o.letter.volume
    r['letter'] = o.letter.number
    if o.letter.period :
      r['period'] = o.letter.period.name
    r['date'] = o.letter.date
    r['word'] = o.word.name
    r['sentence'] = ellipse(o.letter.text[o.sentence.start_position:o.start_position-1],
                     o.letter.text[o.start_position:o.end_position], 
                     o.letter.text[o.end_position+1:o.sentence.end_position])
    answer.append(r)
  return answer

@json_cache
def occurrences_index(request, pks) :
  pks = map(int,pks.split(','))
  occs = Occurrence.objects.filter(pk__in=pks)
  answer = build_occurrence_table(pks)
  return json.dumps({ 'aaData' : answer }, default=date_handler)

@json_cache
def participe(request) :
  occs = Occurrence.objects.filter(tag__name='participe')
  answer = build_occurrence_table(occs)
  return json.dumps({ 'aaData' : answer }, default=date_handler)

@json_cache
def participe_forward_tree(request) :
  occs = Occurrence.objects.filter(tag__name='participe')
  return forward_tree(occs)

@json_cache
def participe_backward_tree(request) :
  occs = Occurrence.objects.filter(tag__name='participe')
  return backward_tree(occs)
 
@json_cache
def occurrence_word(request, pk) :
  occs = Occurrence.objects.filter(word__id=pk)
  answer = build_occurrence_table(occs)
  return json.dumps({ 'aaData' : answer }, default=date_handler)

@json_cache
def occurrence_family(request, pk) :
  occs = Occurrence.objects.filter(family_id=pk)
  answer = build_occurrence_table(occs)
  return json.dumps({ 'aaData' : answer }, default=date_handler)

def forward_tree(occs) :
  st = SuffixTree()
  for o in occs:
    nexts = Occurrence.objects.filter(sentence_id=o.sentence.id).order_by('start_position').filter(start_position__gte=o.start_position).select_related('word')
    l = [x.word.name for x in nexts]
    st.add(l)
  return st.json()

def backward_tree(occs) :
  st = SuffixTree()
  for o in occs:
    nexts = Occurrence.objects.filter(sentence_id=o.sentence.id).order_by('-start_position').filter(start_position__lte=o.start_position).select_related('word')
    l = [x.word.name for x in nexts]
    st.add(l)
  return st.json()

@json_cache
def word_forward_tree(request, pk) :
  occs = Occurrence.objects.filter(word__id=pk)
  return forward_tree(occs)

@json_cache
def word_backward_tree(request, pk) :
  occs = Occurrence.objects.filter(word__id=pk)
  return backward_tree(occs)

@json_cache
def family_forward_tree(request, pk) :
  occs = Occurrence.objects.filter(family__id=pk)
  return forward_tree(occs)

@json_cache
def family_backward_tree(request, pk) :
  occs = Occurrence.objects.filter(family__id=pk)
  return backward_tree(occs)

@json_cache
def index_word(request) : 
 # objects = Word.objects.annotate(occurrences=Count('occurrence')).order_by('pk')
  occs = Occurrence.objects.all().select_related('word')
  occurrences = Counter()
  letters = defaultdict(set)
  answer = list()
  for o in occs :
    occurrences[o.word]+=1
    letters[o.word].add(o.letter_id)
  for o in letters:
    r = dict()
    r['link'] = reverse('occurrence-word', args=(o.pk,))
    r['name'] = o.name
    r['family'] = o.family.name
    r['occurrences'] = occurrences[o]
    r['docfreq'] = len(letters[o])
    answer.append(r)

  return json.dumps({ 'aaData' : answer })

@json_cache
def index_family(request) : 
  objects = Family.objects.annotate(occurrences=Count('word__occurrence')).order_by('pk')
  size_all = Occurrence.objects.count()
  size_ign = Occurrence.objects.exclude(word__family__name__contains = "IGNORED").count()
  answer = list()
  for o in objects :
    r = dict()
    r['link'] = reverse('occurrence-family', args=(o.pk,))
    r['name'] = o.name
    r['size'] = Word.objects.filter(family_id = o.id).count()
    r['occurrences'] = o.occurrences
    r['frequence'] = "{0:2.2f}".format(float(o.occurrences) * 100.0 / float(size_all))
    r['frequence-ign'] = "{0:2.2f}".format(float(o.occurrences) * 100.0 / float(size_ign))

    # Occurrence.objects.filter(word__family__id = o.id).count()
    answer.append(r)
  return json.dumps({'aaData' : answer })

@json_cache
def index_period(request) : 
  objects = Period.objects.order_by('pk')
  answer = list()
  cpt = 1
  for o in objects :
    r = dict()
    r['id'] = cpt
    r['content'] = o.name
    r['start'] = datetime.combine(o.start, time.min)
    r['end'] = datetime.combine(o.end, time.max)
    answer.append(r)
    cpt+=1
  letters = Letter.objects.order_by('pk')
  for l in letters : 
    if l.date :
      r = dict()
      r['id'] = cpt
      r['content'] = "{0}@{1}".format(l.number,l.volume)
      r['start'] = l.date
      answer.append(r)
      cpt+=1

  return json.dumps({ 'aaData' : answer }, default=date_handler)


@json_cache
def index_francia(request) : 
  francia =  Occurrence.objects.filter(letter__period__name__icontains="franc").select_related('word__family')
  words = dict()
  count = dict()
  count_all = dict()
  for o in francia.all() :
    name = o.word.family.name
    if name in words:
      words[name] += 1
    else : 
      words[name] = 1
      count[name] = francia.filter(word__family__id = o.word.family.id).count()
      count_all[name] = Occurrence.objects.filter(word__family__id = o.word.family.id).count()
  size_francia = francia.count()
  size_francia_ign = francia.exclude(word__family__name__contains = "IGNORED").count()
  size_all = Occurrence.objects.count()
  size_all_ign = Occurrence.objects.exclude(word__family__name__contains = "IGNORED").count()
  answer = list()
  for w in words :
    r = dict()
    frq = float(count[w]) * 100.0 / float(size_francia)
    frq_ign = float(count[w]) * 100.0 / float(size_francia_ign)
    frq_all = float(count_all[w]) * 100.0 / float(size_all)
    frq_all_ign = float(count_all[w]) * 100.0 / float(size_all_ign)

    rapport = (float(count[w]) * float(size_all)) / (float(count_all[w])*float(size_francia))
    rapport_ign = (float(count[w]) * float(size_all_ign)) / (float(count_all[w])*float(size_francia_ign))
    r['name'] = w
    r['count'] = count[w]
    r['frequence'] = "{0:.2f}".format(frq)
    r['frequence_ign'] = "{0:.2f}".format(frq_ign)
    r['count_all'] = count_all[w]
    r['frequence_all'] = "{0:2.2f}".format(frq_all)
    r['frequence_all_ign'] = "{0:2.2f}".format(frq_all_ign)
    r['diff'] = "{0:.3f}".format(frq - frq_all)
    r['diff_ign'] = "{0:.3f}".format(frq_ign - frq_all_ign)
    r['rapport'] = "{0:.3f}".format(rapport)
    r['rapport_ign'] = "{0:.3f}".format(rapport_ign)
    r['chaton'] = "{0:.3f}".format(math.pow(rapport_ign,2)*math.sqrt(count[w]))
    answer.append(r)

  return json.dumps({
      'size_francia' : size_francia,
      'size_all' : size_all, 
      'size_rate': float(size_all) / float(size_francia),
      'aaData' : answer }, default=date_handler)

@json_cache
def index_quote(request) : 
  letters =  Letter.objects.filter(period__name__icontains="franc").filter(Q(text__contains="«") | Q(text__contains="\"") | Q(text__contains="''")).annotate(length=Count('occurrence')).order_by('pk')
  answer = list()
  for l in letters :
    r = dict()
    r['link'] = reverse('letter', args=(l.pk,))
    r['modal'] = reverse('modal-letter', args=(l.pk,))
    r['volume'] = l.volume
    r['number'] = l.number
    r['length'] = l.length
    r['date'] = l.date
    if l.period : 
      r['period'] = l.period.name
    else : 
      r['period'] = ''
    answer.append(r)

  return json.dumps({ 'aaData' : answer }, default=date_handler)

class QuoteView(generic.TemplateView):
  template_name = 'browser/quote.html'

class IndexView(generic.TemplateView):
  template_name = 'browser/index.html'

class ParticipeView(generic.TemplateView):
  template_name = 'browser/participe.html'

class WordView(generic.TemplateView):
  template_name = 'browser/index-word.html'

class OccurrenceWordView(generic.DetailView):
  model = Word
  template_name = 'browser/index-occurrence-word.html'

class OccurrenceFamilyView(generic.DetailView):
  model = Family
  template_name = 'browser/index-occurrence-family.html'

class FamilyView(generic.TemplateView):
  template_name = 'browser/index-family.html'

class LetterView(generic.DetailView):
  model = Letter
  template_name = 'browser/detail.html'

class PeriodView(generic.TemplateView):
  template_name = 'browser/index-period.html'

class FranciaView(generic.TemplateView):
  template_name = 'browser/index-francia.html'

class ModalLetterView(generic.DetailView):
  model = Letter
  template_name = 'browser/modal-letter.html'

class ZipfView(generic.TemplateView):
  template_name = 'browser/zipflaw.html'
