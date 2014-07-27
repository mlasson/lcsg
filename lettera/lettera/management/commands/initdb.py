import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family, Sentence
from optparse import make_option
from itertools import tee

# checker les bornes

contractions = ['l', 's', 't', 'dell', 'l', 'all', 'sull', 'c', 'd', 'nell']
def split_contraction(string, start, end):
  splitname = string.split("'")

  if len(splitname) == 0:
    logging.warning('Zero contraction: \"{0}\"'.format(splitname))
    return []
  if splitname == ['']: 
    logging.warning('Zero contraction: \"{0}\"'.format(splitname))
    return []
  if splitname[0] == '':
    splitname = splitname[1:]
    splitname[0] = "'"+splitname[0]
  if splitname[-1] == '':
    splitname = splitname[:-1]
    splitname[-1] = splitname[0]+"'"
  if len(splitname) > 2:
    logging.warning('Multiple contraction: \"{0}\"'.format(splitname))
    return []
  if len(splitname) == 2:
    front, back = splitname
    if front in contractions :
      return [(front+"'", start, start+len(front)+1), (back, start+len(front)+2, end)]
    else :
      return [(string, start, end)]       
  return [(string, start, end)]



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
    print('Clearing sentences ...')
    Sentence.objects.all().delete()
    print('Filling sentences ...')
    sentences = list()
    for l in all_letters:
      sys.stdout.write("%5d / %d\r" % (cpt, max))
      sys.stdout.flush()
      cpt = cpt + 1
      phrases = l.text.lower().split('.')
      start_position = 0
      for phrase in phrases:
        end_position = start_position + len(phrase)+1
        sentence = Sentence(letter=l, start_position=start_position, end_position=end_position)
        sentences.append(sentence)
        start_position = end_position
    print('Saving sentences ...')
    Sentence.objects.bulk_create(sentences)
    sentences=list(Sentence.objects.all())
    print('Filling the base of occurrences ...') 
    Occurrence.objects.all().delete()
    cpt = 0
    for l in all_letters:
      sys.stdout.write("%5d / %d\r" % (cpt, max))
      sys.stdout.flush()
      cpt = cpt + 1
      phrases = l.text.lower().split('.')
      position = 0
      num = 0
      for phrase in phrases:
        sentence = next ((x for x in sentences if (x.letter_id == l.id and 
                                         x.start_position >= position and 
                                         position <= x.end_position)), None)
        if not sentence:
            print('Bug : phantom sentence ?', position, len([x for x in sentences if x.letter_id == l.id]))
            continue
        for m in re.finditer("(([^\W\d]|')+)", phrase):
          namelist = split_contraction(m.group(0), position+m.start(), position+m.end())
          for name, start, end in namelist:
            try :
              word = dic_words[name]
            except KeyError :
              word = Word(name=name, family=ignored_family)
              word.save()
              dic_words[name] = word
              ignored.add(name)
            occ = Occurrence(word=word, family_id=word.family_id, letter=l,sentence=sentence,start_position=start, end_position=end)
            occurrences.append(occ)
        position += len(phrase)+1
    if len(ignored) > 0:
      logging.warning('Beware the following words have been ignored:\n'+', '.join(list(ignored)))
    print('Writing to the database all occurrences ...')
    Occurrence.objects.bulk_create(occurrences)
