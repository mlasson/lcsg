import re, logging, browser, sys, math
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from browser.models import Letter, Period, Word, Occurrence, Family, Tag, Sentence, Frequency
from optparse import make_option
from itertools import tee
from collections import Counter, defaultdict
from django.db.models import Q


class Command(BaseCommand):
    args = '<???>'
    help = 'Filter empty and unused families'

    def handle(self, *args, **options):
        empty_families = Family.objects.annotate(cnt=Count('word')).filter(cnt=0)
        print('\nThe following families are empty:')
        print(', '.join(map(str, empty_families)))
        print(empty_families.count())
        empty_families.delete()
        
        noocc_families = Family.objects.annotate(cnt=Count('occurrence')).filter(cnt=0)
        print('The following families never occur:')
        print(', '.join(map(str, noocc_families)))
        print(noocc_families.count())
        noocc_families.delete()
