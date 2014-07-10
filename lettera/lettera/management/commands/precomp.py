import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family, Tag, Sentence
from optparse import make_option
from itertools import tee
from collections import defaultdict

max_dist = 1

class Command(BaseCommand):
  args = '<???>'
  help = 'Do some post-treatments on the database'

  def handle(self, *args, **options):
    print('Retrieve occurrences ...')
    occurrences = Occurrence.objects.order_by('letter', 'start_position').select_related('word', 'sentence')
    print('Sorting occurrences ...')
    occ_sorted=defaultdict(list)
    cpt = 0
    max = len(occurrences)
    for x in occurrences:
      if cpt % 10 == 0 :
        sys.stdout.write("%5d / %d\r" % (cpt, max))
        sys.stdout.flush()
      cpt += 1
      occ_sorted[x.sentence_id].append(x)
    print('Drop all tags ...')
    Tag.objects.all().delete()
    def pairwise(it):
      a,b = tee(it)
      next(b,None)
      return zip(a,b)
    cpt = 0
    tags = list()
    dist = 0
    for l in occ_sorted.values():
      found = False
      essere = False
      for x in l :
        if cpt % 10 == 0 :
          sys.stdout.write("%5d / %d\r" % (cpt, max))
          sys.stdout.flush()
        cpt += 1
        dist += 1
        if dist > max_dist:
            essere = False
        if (x.word.name == 'stato' or x.word.name == 'stati'):
          if essere:
            tag = Tag(occurrence=x, name = 'participe') 
            tags.append(tag)
          found = True
        if (x.word.name in ['è','essere','sono','era','fussi','sia','sonne']
         or x.word.name in ['sono','essere','siamo','sieno','fussino','erano','sendo']):
          essere = True
          dist = 0
    print('\nSaving ...')
    Tag.objects.bulk_create(tags)
    print('\nRetrieve essere')
    essere = Family.objects.get(name='essere')
    print('\nUpdating all participe ...')
    participes = Occurrence.objects.filter(tag__name="participe").update(family=essere)

        
        
