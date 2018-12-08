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
    help = 'Compute inverse and direct frequencies'

    def handle(self, *args, **options):
        print(
            'Checking families that families are not empty and contains at least one occurrence'
        )
        all_families = Family.objects.annotate(
            occurrences=Count('word__occurrence')).order_by('pk')
        maxcpt = all_families.count()
        cpt = 0
        empty_families = list()
        noocc_families = list()
        for f in all_families:
            cpt += 1
            if cpt % 10 == 1:
                sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
                sys.stdout.flush()
            sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
            size = Word.objects.filter(family_id=f.id).count()
            if size == 0:
                empty_families.append(f.name)
                f.delete()
            elif f.occurrences == 0:
                noocc_families.append(f.name)
                f.delete()
        print('\nThe following families are empty:')
        print(', '.join(empty_families))
        print('The following families never occur:')
        print(', '.join(noocc_families))
