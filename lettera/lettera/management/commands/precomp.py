import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family, Tag, Sentence
from optparse import make_option
from itertools import tee
from collections import defaultdict
from django.db.models import Q

max_dist = 3

class Command(BaseCommand):
  args = '<???>'
  help = 'Do some post-treatments on the database'

  def handle(self, *args, **options):
    print('Retrieve occurrences ...')
    occurrences = Occurrence.objects.filter(Q(word__name='stato') | Q(word__name='stati'))
    print(len(occurrences),'occurrences')
    print('Fetch sentences ...')
    sentences = set(x.sentence_id for x in occurrences)
    print(len(sentences),'sentences')
    print('Drop all tags ...')
    Tag.objects.all().delete()
    cpt = 0
    tags = list()
    dist = 0
    max = len(occurrences)
    for s in sentences:
      phrase = Occurrence.objects.filter(sentence__id=s).order_by('start_position').select_related('word')
      found = False
      essere = False
      for x in phrase :
        if cpt % 10 == 0 :
          sys.stdout.write("%5d / %d\r" % (cpt, max))
          sys.stdout.flush()
        cpt += 1
        dist += 1
        if dist > max_dist:
            essere = False
        if (x.word.name == 'stato' 
         or x.word.name == 'stati'):
          if essere and dist == 2:
            tag = Tag(occurrence=x, name = 'participe') 
            tags.append(tag)
          found = True
        if (x.word.name in ['è','essere','sono','era','fussi','sia','sonne']
         or x.word.name in ['sono','essere','siamo','sieno','fussino','erano','sendo']):
          essere = True
          dist = 0
    print('\nSaving ...')
    Tag.objects.bulk_create(tags)
    print('Retrieve essere')
    essere = Family.objects.get(name='essere')
    print('Updating all participe ...')
    participes = Occurrence.objects.filter(tag__name="participe").update(family=essere)

        
        
