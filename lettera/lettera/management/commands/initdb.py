import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family
from optparse import make_option


class Command(BaseCommand):
  args = '<???>'
  help = 'Initialize the database'

  def handle(self, *args, **options):
    ignored = set()
    occurrences = list()
    all_letters = Letter.objects.all()
    all_words = Word.objects.all()
    dic_words = dict()
    print('Organizing words into a dictionarry ...') 
    for w in all_words:
      dic_words[w.name] = w
    print('Creating the family of ignored words ...') 
    ignored_family = Family(name="IGNORED WORDS")
    ignored_family.save()
    max = len(all_letters)
    cpt = 0
    print('Filling the base of occurrences ...') 
    for l in all_letters:
      sys.stdout.write("%5d / %d\r" % (cpt, max))
      sys.stdout.flush()
      cpt = cpt + 1
      for m in re.finditer("[^\W\d]+", l.text.lower()):
        name = m.group(0)
        try :
          word = dic_words[name]
        except KeyError :
          word = Word(name=name, family=ignored_family)
          word.save()
          dic_words[name] = word
          ignored.add(name)
        occ = Occurrence(word=word, letter=l,start_position=m.start(), end_position=m.end())
        occurrences.append(occ)
    if len(ignored) > 0:
      logging.warning('Beware the following words have been ignored:\n'+', '.join(list(ignored)))
    print('Writing to the database all occurrences ...')
    Occurrence.objects.bulk_create(occurrences)
