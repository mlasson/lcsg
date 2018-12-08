import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family, Sentence
from optparse import make_option
from itertools import tee

splitting = [
    x.split("'") for x in [
        "quell'acqua", "quell'altro", "quell'oche", "quell'ora",
        "qualch'altra", "quest'altra", "quest'altri", "quest'altro",
        "quest'anno", "alcun'altra", "anch'egli", "ch'altro", "egl'imborsorno",
        "mill'altre", "mill'anni", "un'ora", "ch'e'", "ch'è", "ch'egli",
        "ch'ella", "ch'elle", "ch'era", "ch'erano", "ch'erono", "ch'io",
        "coll'altre", "coll'artiglieria", "coll'aspro", "coll'oratore",
        "dall'altra", "dall'altre", "dall'altro", "dall'assedio", "dall'isola",
        "dall'orecchie", "dall'un", "dall'uno", "dagl'inganni", "un'altra",
        "gl'impicassino", "e'capituli", "bell'agio", "buon'ora", "ogn'altra",
        "ogn'altro"
    ]
]

resplit = {"quelloche": ["quell", "oche"]}

ignored_words = [
    "za", "rza", "zz", "z", "vd", "tt", "tti", "tto", "trebbe", "u", "uae",
    "ui", "q", "pp", "pre", "p", "pa", "pe", "pau", "¼", "½", "¾", "'", "am",
    "annotation", "b", "ar", "anzesi", "bb", "be", "bi", "bil", "bo", "bu",
    "c", "ca", "can", "cap", "ce", "cer", "ch", "eo", "er", "enza", "fo", "g",
    "à", "f", "segu", "vu", "sig", "avvel", "ri", "seu", "vuo", "ga", "ge",
    "gg ", "ggono", "ghe", "gu", "gi", "f", "ea", "eam", "iacozo", "ian",
    "ibi", "ic", "id", "ie", "ier", "is", "fotocopia", "h", "ing", "ipotizzo",
    "mec", "gie", "gié", "gio", "l", "lisogno", "mei", "men", "nc", "nde",
    "nic", "ro", "rr", "rra", "nit", "rnerai", "rsenata", "rsino", "rso",
    "rtezze", "rto", "ru", "s", "rza", "sp", "ss", "ssi", "ssimo", "ssino",
    "sub", "t", "ta", "tà", "to", "v", "ve", "du", "taltis", "cho", "cs", "cu",
    "co", "nn", "dd", "dattiloscritto", "d", "ars", "apostrofo", "ac", "ba",
    "deb", "lu", "m", "dim", "nno", "alt", "lla ", "lle ", "do", "ran", "arne",
    "ars", "at", "ate", "aus", "aut", "definitivo", "fam", "gl", "diu", "doc",
    "go", "rem", "quo", "peu", "pi", "pis", "ono", "po", "pu", "nte", "nu",
    "possessivo", "cos", "com", "hi", "gentiè", "empti", "ellissi", "por", "r",
    "ran", "ra", "got", "gl", "go", "gra", "avi", "ese", "deranno", "lli ",
    "berazione", "llo", "n", "frase", "nos", "mm", "mo", "ms", "mu", "na",
    "tei", "tel", "mova", "'n", "par", "vis", "vo'", "eti", "an", "ab", "aer",
    "ag", "ana", "angiolinum", "banderiis", "leo", "sal", "sel", "º", "ob",
    "oc", "fi", "í", "ni", "en", "montes", "ì", "h'", "gg", "gu", "lla", "tis",
    "lle", "abis", "di'", "lli"
]

contractions = [
    'l', 's', 't', 'dell', 'l', 'all', 'sull', 'c', 'd', 'nell', 'ch'
]


# checker les bornes
def split_contraction(string, start, end):
    try:
        splitname = resplit[string]
    except KeyError:
        splitname = string.split("'")
    if len(string) == 0:
        return []
    if len(splitname) == 0:
        logging.warning('Zero contraction: \"{0}\" in \"{1}\"'.format(
            splitname, string))
        return []
    if splitname[0] == '':
        splitname = splitname[1:]
        splitname[0] = "'" + splitname[0]
    if splitname[-1] == '':
        splitname = splitname[:-1]
        splitname[-1] = splitname[0] + "'"
    if len(splitname) > 3:
        logging.warning('Multiple contraction: \"{0}\"'.format(splitname))
        return []
    if len(splitname) == 3:
        front, middle, back = splitname
        return [(front + "'", start, start + len(front) + 1),
                (middle + "'", start + len(front) + 2,
                 start + len(front) + 2 + len(middle) + 1),
                (back, start + len(front) + 2 + len(middle) + 2, end)]
    if len(splitname) == 2:
        front, back = splitname
        if front in contractions or [front, back] in splitting:
            return [(front + "'", start, start + len(front) + 1),
                    (back, start + len(front) + 2, end)]
        else:
            return [(string, start, end)]
    return [(string, start, end)]


class Command(BaseCommand):
    args = '<???>'
    help = 'Initialize the database'

    def handle(self, *args, **options):
        unknown = set()
        occurrences = list()
        all_letters = Letter.objects.all()
        all_words = Word.objects.all()
        dic_words = dict()
        print('Clearing occurrences ...')
        Occurrence.objects.all().delete()
        print('Organizing words into a dictionarry ...')
        for w in all_words:
            dic_words[w.name] = w
        print('Creating the family of ignored words ...')
        unknown_family = Family(name="IGNORED WORDS")
        unknown_family.save()
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
                end_position = start_position + len(phrase) + 1
                sentence = Sentence(
                    letter=l,
                    start_position=start_position,
                    end_position=end_position)
                sentences.append(sentence)
                start_position = end_position
        print('Saving sentences ...')
        Sentence.objects.bulk_create(sentences)
        sentences = list(Sentence.objects.all())
        print('Filling the base of occurrences ...')
        cpt = 0
        for l in all_letters:
            sys.stdout.write("%5d / %d\r" % (cpt, max))
            sys.stdout.flush()
            cpt = cpt + 1
            phrases = l.text.lower().split('.')
            position = 0
            num = 0
            for phrase in phrases:
                sentence = next(
                    (x for x in sentences
                     if (x.letter_id == l.id and x.start_position >= position
                         and position <= x.end_position)), None)
                if not sentence:
                    print('Bug : phantom sentence ?', position,
                          len([x for x in sentences if x.letter_id == l.id]))
                    continue
                for m in re.finditer("(([^\W\d]|['<>])+)", phrase):
                    name = m.group(0)
                    name = name.replace('<', '')
                    name = name.replace('>', '')
                    if len(name) == 0:
                        logging.warning(
                            'Empty name in : \"{0}\"'.format(phrase))
                    if name in ignored_words:
                        try:
                            word = dic_words[name]
                        except KeyError:
                            word = Word(name=name, family=unknown_family)
                            word.save()
                            dic_words[name] = word
                        continue
                    namelist = split_contraction(name, position + m.start(),
                                                 position + m.end())
                    for name, start, end in namelist:
                        try:
                            word = dic_words[name]
                        except KeyError:
                            word = Word(name=name, family=unknown_family)
                            word.save()
                            dic_words[name] = word
                            unknown.add(name)
                        occ = Occurrence(
                            word=word,
                            family_id=word.family_id,
                            letter=l,
                            sentence=sentence,
                            start_position=start,
                            end_position=end)
                        occurrences.append(occ)
                position += len(phrase) + 1
        if len(unknown) > 0:
            logging.warning(
                'Beware the following words have been classofied:\n' +
                ', '.join(list(unknown)))
        print('Writing to the database all occurrences ...')
        Occurrence.objects.bulk_create(occurrences)
