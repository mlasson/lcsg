import re, logging, browser, sys
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family, Tag, Sentence
from optparse import make_option
from itertools import tee
from collections import defaultdict
from django.db.models import Q

max_dist = 3

before_stato = [
    s.lower() for s in [
        'è', 'e', 'ha', 'essere', 'se\'', 'fussi', 'fosse', 'esserli',
        'esserci', 'esserti', 'tu', 'io', 'sarà', 'saria', 'sarei', 'Èvi',
        'essendo', 'essendoci', 'era', 'erono', 'esserne', 'sarebbe', 'sia',
        'dipoi', 'già', 'ragionamento', 'sono', 'sonne', 'massime', 'ancora',
        'bene', 'sempre', 'mai', 'sendone', 'mattina', 'ventura', 'sendo'
    ]
]
before_stati = [
    'sono', 'essere', 'siamo', 'sieno', 'fussino', 'erano', 'erono', 'eri',
    'sendo', 'siate', 'noi', 'loro', 'ancora', 'dipoi', 'mai', 'suti',
    'sareno', 'mattina', 'esservi', 'disordini', 'orsini', 'ora', 'e', 'non',
    'medesimo'
]

before_passato = [
    s.lower() for s in [
        'e', 'era', 'verno', 'Carlo', 'sendo', 'già', 'è', 'abbino', 'ancora',
        'avevano', 'manca', 'avea', 'sia', 'quando', 'sendo', 'poi', 'abbino',
        'cosi', 'avendo', 'Andrea', 'proxime', 'fussi', 'ha', 'che', 'essere',
        'essendo', 'Spedalingo', 'Signoria', 'ora', 'fussi', 'tornò', 'avere',
        'mattina'
    ]
]
before_passati = [
    'nuovo', 'sono', 'essere', 'prossime', 'sete', 'erano', 'fussino', 'ché',
    'sendo', 'avventura', 'ancora', 'e', 'fanno', 'questa'
]
before_passate = ['erano', 'sono', 'sieno', 'essere']
before_passata = [
    'alla', 'nella', 'è', 'state', 'essendo', 'quella', 'questa', 'fussi',
    'della', 'piena', 'la', 'quale'
]


class Command(BaseCommand):
    args = '<???>'
    help = 'Do some post-treatments on the database'

    def handle(self, *args, **options):
        print('Retrieve occurrences ...')
        occurrences = Occurrence.objects.filter(
            Q(word__name='stato') | Q(word__name='stati')
            | Q(word__name='passati') | Q(word__name='passato')
            | Q(word__name='passata') | Q(word__name='passete'))
        print(len(occurrences), 'occurrences')
        print('Fetch sentences ...')
        sentences = set(x.sentence_id for x in occurrences)
        print(len(sentences), 'sentences')
        print('Drop all tags ...')
        Tag.objects.all().delete()
        tags = list()

        def pairwise(iterable):
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)

        for s in sentences:
            phrase = Occurrence.objects.filter(sentence__id=s).order_by(
                'start_position').select_related('word')
            max = len(phrase)
            for x, y in pairwise(phrase):
                if (y.word.name == 'passato' and x.word.name in before_passato
                        or y.word.name == 'passati'
                        and x.word.name in before_passati
                        or y.word.name == 'passate'
                        and x.word.name in before_passate
                        or y.word.name == 'passata'
                        and x.word.name in before_passata):
                    tag = Tag(occurrence=y, name='passare')
                    tags.append(tag)

                if (y.word.name == 'stato' and x.word.name in before_stato or
                        y.word.name == 'stati' and x.word.name in before_stati
                        or y.word.name == 'stato' and
                    (x.word.name, x.letter.volume, x.letter.number) in [
                        ('discreto', 6, 62), ('montevarchi', 6, 89),
                        ('viniziani', 6, 75), ('che', 5, 68)
                    ]):
                    tag = Tag(occurrence=y, name='participe')
                    tags.append(tag)

        print('Saving ...')
        Tag.objects.bulk_create(tags)
        print('Retrieve essere')
        essere = Family.objects.get(name='essere')
        print('Updating all participe ...')
        participes = Occurrence.objects.filter(tag__name="participe").update(
            family=essere)
        passare = Family.objects.get(name='passare')
        print('Updating all passare ...')
        participes = Occurrence.objects.filter(tag__name="passare").update(
            family=passare)
