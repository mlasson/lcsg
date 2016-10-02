import re, logging, browser, sys, math
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from browser.models import *
from optparse import make_option
from itertools import tee
from collections import Counter, defaultdict
from django.db.models import Q

class Command(BaseCommand):
  args = '<???>'
  help = 'Fill the subcorpus table with periods'

  def handle(self, *args, **options):
    letters = Letter.objects.all()
    result = defaultdict(list)
    Subcorpus.objects.all().delete()
    for l in letters: 
      period = l.period
      if period: 
        result[period.name].append(l.pk)
      else:
        result['SG'].append(l.pk)
      if '"' in l.text or '«' in l.text:
        result['HAS_QUOTES'].append(l.pk)


    subcorpis = []
    for key, value in result.items():
      sc = Subcorpus(name = key, letters=','.join(map(str, value)))
      subcorpis.append(sc)
    Subcorpus.objects.bulk_create(subcorpis)
    ignore_letters = []
    for l in letters:
      if l.ignore :  
        ignore_letters.append(l)
    ignore_corpus = Subcorpus(name = 'Ignore', letters=','.join(map(str, ignore_letters)))
    ignore_corpus.save()

    all_letters = list (l.pk for l in letters)
    all_corpus = Subcorpus(name = 'All',  letters=','.join(map(str, all_letters)))
    all_corpus.save()
