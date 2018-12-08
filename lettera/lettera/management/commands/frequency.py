import re, logging, browser, sys, math
from django.core.management.base import BaseCommand, CommandError
from browser.models import Letter, Period, Word, Occurrence, Family, Tag, Sentence, Frequency
from optparse import make_option
from itertools import tee
from collections import Counter, defaultdict
from django.db.models import Q


class Command(BaseCommand):
    args = '<???>'
    help = 'Compute inverse and direct frequencies'

    def handle(self, *args, **options):
        occs = Occurrence.objects.all()
        datas = defaultdict(Counter)
        sizes = Counter()
        idf = defaultdict(set)

        print('Drop all previous information ...')
        Frequency.objects.all().delete()
        print('Counting occurrences ...')
        maxcpt = occs.count()
        cpt = 0
        for x in occs:
            cpt += 1
            if cpt % 1000 == 1:
                sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
                sys.stdout.flush()
            datas[x.letter_id][x.family_id] += 1
            sizes[x.letter_id] += 1
            idf[x.family_id].add(x.letter_id)
        sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
        N = len(sizes)
        cpt = 0
        freqs = list()
        print('\nUpdating families with idf')
        maxcpt = Family.objects.count()
        cpt = 0
        for x in Family.objects.all():
            cpt += 1
            if cpt % 10 == 1:
                sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
                sys.stdout.flush()
            len_idf = len(idf[x.id])
            if len_idf > 0:
                x.idf = math.log(float(N) / len_idf)
                x.df = len_idf
                x.save()
        sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
        cpt = 0
        print('\nComputing frequencies ...')
        for d, terms in datas.items():
            cpt += 1
            sys.stdout.write("%6d / %d\r" % (cpt, N))
            sys.stdout.flush()
            size = sizes[d]
            maxf = terms.most_common(1)[0][1]
            for t, n in terms.items():
                raw = float(n) / size
                if n > 0:
                    logarithmic = 1 + math.log(raw)
                else:
                    logarithmic = 0
                augmented = 0.5 + (0.5 * n) / maxf
                freq = Frequency(
                    family_id=t,
                    letter_id=d,
                    raw=raw,
                    logarithmic=logarithmic,
                    augmented=augmented)
                freqs.append(freq)
        periods = Period.objects.all()
        maxcpt = periods.count()
        cpt = 0
        for p in periods:
            cpt += 1
            sys.stdout.write("%6d / %d\r" % (cpt, N))
            sys.stdout.flush()
            size = Occurrence.objects.all().select_related('letter').filter(
                letter__period_id=p.pk).count()
            p.size = size
            p.save()
        sys.stdout.write("\r%6d / %d" % (cpt, maxcpt))
        print('\nSaving ...')
        Frequency.objects.bulk_create(freqs)
