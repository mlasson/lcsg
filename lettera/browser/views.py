import json
import math
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.db.models import Count
from django.db.models import query
from django.shortcuts import render
from django.http import HttpResponse 
from django.views import generic
from browser.models import Letter, Occurrence, Word, Family, Period, Cache
from django.core.paginator import Paginator

class json_cache(object):
  def __init__(self, func):
    self.func = func
    self.name = func.__name__
    
  def __call__(self, arg, **args):
    try :
      result = Cache.objects.get(name = self.name, args = repr(arg.path)).value
      print ('!!! using cache for '+self.name+'\n')
    except Cache.objects.model.DoesNotExist:
      result = self.func(arg, **args)
      new_entry = Cache(name=self.name, args=repr(arg.path), value = result)
      new_entry.save()
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
def index_occurrences(request, pk) : 
  objects = Occurrence.objects.filter(letter_id = pk).order_by('pk')
  answer = list()
  for o in objects :
    r = dict()
    r['word'] = o.word.name
    r['letter'] = o.letter.pk 
    r['start_position'] = o.start_position
    r['end_position'] = o.end_position
    r['family'] = o.word.family.name
    answer.append(r)

  return json.dumps({ 'aaData' : answer })

@json_cache
def index_word(request) : 
  objects = Word.objects.annotate(occurrences=Count('occurrence')).order_by('pk')
  answer = list()
  for o in objects :
    r = dict()
    r['name'] = o.name
    r['family'] = o.family.name
    r['occurrences'] = o.occurrences
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
    r['start'] = o.start
    r['end'] = o.end
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

  #return HttpResponse(json.dumps({
  #    'size_francia' : size_francia,
  #    'size_all' : size_all, 
  #    'size_rate': float(size_all) / float(size_francia),
  #    'aaData' : answer }, default=date_handler), content_type='application/javascript')
  return json.dumps({
      'size_francia' : size_francia,
      'size_all' : size_all, 
      'size_rate': float(size_all) / float(size_francia),
      'aaData' : answer }, default=date_handler)

class IndexView(generic.TemplateView):
  template_name = 'browser/index.html'

class WordView(generic.TemplateView):
  template_name = 'browser/index-word.html'

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
