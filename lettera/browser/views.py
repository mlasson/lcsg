import json
import math
from datetime import datetime, time, date
from collections import Counter, defaultdict
from django.urls import reverse
from django.template import RequestContext, loader
from django.db.models import Count, Q, query
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.decorators import login_required
from browser.models import *
from django.core.paginator import Paginator
from utils.suffixtree import SuffixTree
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from browser.corpus import Corpus
from browser import corpus

class json_cache(object):
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __call__(self, arg, **args):
        input_data = arg.path
        if arg.method == 'POST' and arg.body:
            input_data += arg.body.decode()
        query = Cache.objects.filter(
            name=self.name, args=repr(input_data)).first()
        if not query:
            result = self.func(arg, **args)
            if result:
                new_entry = Cache(name=self.name, args=repr(input_data), value=result)
                new_entry.save()
        else:
            result = query.value
        return HttpResponse(result, content_type='application/javascript')


class json_nocache(object):
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __call__(self, arg, **args):
        result = self.func(arg, **args)
        return HttpResponse(result, content_type='application/javascript')


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError(
            'Object of type %s with value of %s is not JSON serializable' %
            (type(obj), repr(obj)))


@json_cache
def index_letter(request, letters=None):
    objects = Letter.objects.annotate(
        length=Count('occurrence')).order_by('pk')
    answer = list()
    if letters:
        letters = [int(pk) for pk in letters.split(',')]
        objects = [l for l in objects if l.pk in letters]
    for l in objects:
        r = dict()
        r['pk'] = l.pk
        r['link'] = reverse('letter', args=(l.pk, ))
        r['modal'] = reverse('modal-letter', args=(l.pk, ))
        r['volume'] = l.volume
        r['number'] = l.number
        r['length'] = l.length
        r['date'] = l.date
        if l.period:
            r['period'] = l.period.name
        else:
            r['period'] = ''

        answer.append(r)

    return json.dumps({'aaData': answer}, default=date_handler)


@json_cache
def letters_from_date(request, start, end):
    try:
        [year, month, day] = map(int, start.split('-'))
        start = date(year, month, day)
        [year, month, day] = map(int, end.split('-'))
        end = date(year, month, day)
        objects = Letter.objects.all()
        result = []
        for l in objects:
            if l.date and start <= l.date and l.date <= end:
                result.append(l.pk)
        return json.dumps(result)
    except ValueError:
        return json.dumps([])


def index_letter_subcorpus(request, subcorpus):
    return index_letter(
        request, letters=Subcorpus.objects.filter(name=subcorpus)[0].letters)


@json_cache
def occurrences_letter(request, pk):
    objects = Occurrence.objects.filter(
        letter_id=pk).order_by('pk').select_related('family', 'word')
    answer = list()
    for o in objects:
        r = dict()
        r['word'] = o.word.name
        r['letter'] = o.letter_id
        r['start_position'] = o.start_position
        r['end_position'] = o.end_position
        r['family'] = o.family.name
        answer.append(r)

    return json.dumps({'aaData': answer})


@json_cache
def sentence(request, pk):
    sentence = Sentence.objects.get(pk=pk)
    letter = sentence.letter
    phrase = letter.text[sentence.start_position:sentence.end_position]
    return json.dumps(phrase)


def ellipse(front, word, back, maxsize=100):
    size = len(front) + len(word) + len(back)
    half = int((maxsize - len(word)) / 2)
    diff = size - maxsize
    if diff > 0:
        if len(front) < half:
            back = back[0:maxsize + len(back) - size] + u' …'
        elif len(back) < half:
            front = u'… ' + front[-maxsize - len(front) + size:]
        else:
            back = back[:half] + u' …'
            front = u'… ' + front[-half:]
    return (front, word, back)


def build_occurrence_table(occs):
    answer = list()
    occs = occs.select_related('word', 'sentence', 'letter')
    for o in occs:
        r = dict()
        r['link'] = (reverse('modal-letter', args=(o.letter_id, )),
                     o.start_position, o.end_position)
        r['pk'] = o.letter_id
        r['volume'] = o.letter.volume
        r['letter'] = o.letter.number
        if o.letter.period:
            r['period'] = o.letter.period.name
        r['date'] = o.letter.date
        r['word'] = o.word.name
        r['sentence'] = ellipse(
            o.letter.text[o.sentence.start_position:o.start_position - 1],
            o.letter.text[o.start_position:o.end_position],
            o.letter.text[o.end_position + 1:o.sentence.end_position])
        answer.append(r)
    return answer


@json_cache
def occurrences_index(request, pks):
    pks = map(int, pks.split(','))
    # occs = Occurrence.objects.filter(pk__in=pks)
    answer = build_occurrence_table(pks)
    periods = dict()
    for p in Period.objects.all():
        periods[p.name] = p.size
    periods['SG'] = Occurrence.objects.all().select_related('letter').filter(
        letter__period=None).count()
    return json.dumps({
        'aaData': answer,
        'periods': periods
    },
                      default=date_handler)


@json_cache
def participe(request):
    occs = Occurrence.objects.filter(tag__name='participe')
    answer = build_occurrence_table(occs)
    return json.dumps({'aaData': answer}, default=date_handler)


@json_cache
def participe_forward_tree(request):
    occs = Occurrence.objects.filter(tag__name='participe')
    return forward_tree(occs)


@json_cache
def participe_backward_tree(request):
    occs = Occurrence.objects.filter(tag__name='participe')
    return backward_tree(occs)


@json_cache
def occurrence_word(request, pk):
    occs = Occurrence.objects.filter(word__id=pk)
    answer = build_occurrence_table(occs)
    return json.dumps({'aaData': answer}, default=date_handler)


@json_cache
def occurrence_family(request, pk):
    occs = Occurrence.objects.filter(family_id=pk)
    answer = build_occurrence_table(occs)
    periods = dict()
    for p in Period.objects.all():
        periods[p.name] = p.size
    periods['SG'] = Occurrence.objects.all().select_related('letter').filter(
        letter__period=None).count()
    return json.dumps({
        'aaData': answer,
        'periods': periods
    },
                      default=date_handler)


def forward_tree(occs):
    st = SuffixTree()
    for o in occs:
        nexts = Occurrence.objects.filter(
            sentence_id=o.sentence.id).order_by('start_position').filter(
                start_position__gte=o.start_position).select_related('word')
        l = [x.word.name for x in nexts]
        st.add(l)
    return st.json()


def backward_tree(occs):
    st = SuffixTree()
    for o in occs:
        nexts = Occurrence.objects.filter(
            sentence_id=o.sentence.id).order_by('-start_position').filter(
                start_position__lte=o.start_position).select_related('word')
        l = [x.word.name for x in nexts]
        st.add(l)
    return st.json()


@json_cache
def word_forward_tree(request, pk):
    occs = Occurrence.objects.filter(word__id=pk)
    return forward_tree(occs)


@json_cache
def word_backward_tree(request, pk):
    occs = Occurrence.objects.filter(word__id=pk)
    return backward_tree(occs)


@json_cache
def family_forward_tree(request, pk):
    occs = Occurrence.objects.filter(family__id=pk)
    return forward_tree(occs)


@json_cache
def family_backward_tree(request, pk):
    occs = Occurrence.objects.filter(family__id=pk)
    return backward_tree(occs)


@json_cache
def index_word(request):
    # objects = Word.objects.annotate(occurrences=Count('occurrence')).order_by('pk')
    occs = Occurrence.objects.all().select_related('word')
    occurrences = Counter()
    letters = defaultdict(set)
    answer = list()
    for o in occs:
        occurrences[o.word] += 1
        letters[o.word].add(o.letter_id)
    for o in letters:
        r = dict()
        r['link'] = reverse('occurrence-word', args=(o.pk, ))
        r['name'] = o.name
        r['family'] = o.family.name
        r['occurrences'] = occurrences[o]
        r['docfreq'] = len(letters[o])
        answer.append(r)

    return json.dumps({'aaData': answer})


@json_cache
def index_period(request):
    objects = Period.objects.order_by('pk')
    answer = list()
    cpt = 1
    for o in objects:
        r = dict()
        r['id'] = cpt
        r['content'] = o.name
        r['start'] = datetime.combine(o.start, time.min)
        r['end'] = datetime.combine(o.end, time.max)
        answer.append(r)
        cpt += 1

    return json.dumps({'aaData': answer}, default=date_handler)


@json_cache
def index_francia(request):
    francia = Occurrence.objects.filter(
        letter__period__name__icontains="franc").select_related('word__family')
    words = dict()
    count = dict()
    count_all = dict()
    for o in francia.all():
        name = o.word.family.name
        if name in words:
            words[name] += 1
        else:
            words[name] = 1
            count[name] = francia.filter(
                word__family__id=o.word.family.id).count()
            count_all[name] = Occurrence.objects.filter(
                word__family__id=o.word.family.id).count()
    size_francia = francia.count()
    size_francia_ign = francia.exclude(
        word__family__name__contains="IGNORED").count()
    size_all = Occurrence.objects.count()
    size_all_ign = Occurrence.objects.exclude(
        word__family__name__contains="IGNORED").count()
    answer = list()
    for w in words:
        r = dict()
        frq = float(count[w]) * 100.0 / float(size_francia)
        frq_ign = float(count[w]) * 100.0 / float(size_francia_ign)
        frq_all = float(count_all[w]) * 100.0 / float(size_all)
        frq_all_ign = float(count_all[w]) * 100.0 / float(size_all_ign)

        rapport = (float(count[w]) * float(size_all)) / (
            float(count_all[w]) * float(size_francia))
        rapport_ign = (float(count[w]) * float(size_all_ign)) / (
            float(count_all[w]) * float(size_francia_ign))
        r['name'] = w
        r['count'] = count[w]
        r['frequence'] = "{0:.2f}".format(frq)
        r['frequence_ign'] = "{0:.2f}".format(frq_ign)
        r['count_all'] = count_all[w]
        r['frequence_all'] = "{0:2.2f}".format(frq_all)
        r['frequence_all_ign'] = "{0:2.2f}".format(frq_all_ign)
        r['diff'] = "{0:.3f}".format(frq - frq_all)
        r['diff_ign'] = "{0:.3f}".format(frq_ign - frq_all_ign)
        r['rapport'] = "{0:.3f}".format(rapport)
        r['rapport_ign'] = "{0:.3f}".format(rapport_ign)
        r['chaton'] = "{0:.3f}".format(
            math.pow(rapport_ign, 2) * math.sqrt(count[w]))
        answer.append(r)

    return json.dumps({
        'size_francia': size_francia,
        'size_all': size_all,
        'size_rate': float(size_all) / float(size_francia),
        'aaData': answer
    },
                      default=date_handler)


@json_cache
def index_quote(request):
    letters = Letter.objects.filter(period__name__icontains="franc").filter(
        Q(text__contains="«")
        | Q(text__contains="\"") | Q(text__contains="''")).annotate(
            length=Count('occurrence')).order_by('pk')
    answer = list()
    for l in letters:
        r = dict()
        r['link'] = reverse('letter', args=(l.pk, ))
        r['modal'] = reverse('modal-letter', args=(l.pk, ))
        r['volume'] = l.volume
        r['number'] = l.number
        r['length'] = l.length
        r['date'] = l.date
        if l.period:
            r['period'] = l.period.name
        else:
            r['period'] = ''
        answer.append(r)

    return json.dumps({'aaData': answer}, default=date_handler)


@json_nocache
def create_subcorpus_full(request, ident, letters):
    existing = Subcorpus.objects.filter(name=ident)
    if existing:
        return "The corpus '{0}' already exists.".format(ident)
    subcorpus = Subcorpus(name=ident, letters=letters)
    subcorpus.save()
    return "OK"


@ensure_csrf_cookie
def create_subcorpus(request):
    body = request.body.decode()
    corpi = json.loads(body)
    name = corpi['name']
    letters = ','.join(map(str, corpi['letters']))
    existing = Subcorpus.objects.filter(name=name)
    if existing:
        return HttpResponse("The corpus '{0}' already exists.".format(name))
    subcorpus = Subcorpus(name=name, letters=letters)
    subcorpus.save()
    return HttpResponse("OK")


class HypertestView(generic.TemplateView):
    template_name = 'browser/hypertest.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HypertestView, self).dispatch(*args, **kwargs)


def hypertest_histogram(request):
    if request.method == 'POST' and request.body:
        body = request.body.decode()
        json_request = json.loads(body)

        N = json_request['N'] or 100
        n = json_request['n'] or 10
        K = json_request['K'] or 30
    else:
        N = 100
        n = 10
        K = 30

    answer = corpus.histogram_hypertest(N, n, K)

    return HttpResponse(json.dumps(answer))


def search_subcorpus(request):
    corpus = Corpus()
    body = request.body.decode()
    json_request = json.loads(body)
    search = json_request['search']
    search_mode = json_request['search_mode']
    if search_mode == "family":
        answer = corpus.search_family_letters(search)
    else:
        answer = corpus.search_word_letters(search)

    return HttpResponse(json.dumps(answer))


@json_cache
def index_families_post(request):
    corpus = Corpus()
    if request.method == 'POST' and request.body:
        body = request.body.decode()
        json_request = json.loads(body)
        subcorpus_id = json_request['subcorpus']
        if subcorpus_id is None:
            subcorpus_id = Subcorpus.objects.get(name='All').pk
        return json.dumps(corpus.subcorpus_statistics(subcorpus_id))


@ensure_csrf_cookie
def delete_subcorpus(request):
    body = request.body.decode()
    corpi = json.loads(body)
    pk = int(corpi['pk'])
    Subcorpus.objects.filter(pk=pk).delete()
    return HttpResponse("OK")


@json_nocache
def get_subcorpi(request):
    subcorpi = Subcorpus.objects.all()
    result = []
    try:

        def is_int(x):
            try:
                int(x)
                return True
            except ValueError:
                return False

        for c in subcorpi:
            l = list(int(x) for x in c.letters.split(',') if is_int(x))
            result.append({'pk': c.pk, 'name': c.name, 'letters': l})
        return json.dumps(result)
    except ValueError:
        return json.dumps(result)


class QuoteView(generic.TemplateView):
    template_name = 'browser/quote.html'


class IndexView(generic.TemplateView):
    template_name = 'browser/index.html'

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


class ParticipeView(generic.TemplateView):
    template_name = 'browser/participe.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ParticipeView, self).dispatch(*args, **kwargs)


class WordView(generic.TemplateView):
    template_name = 'browser/index-word.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WordView, self).dispatch(*args, **kwargs)


class OccurrenceWordView(generic.DetailView):
    model = Word
    template_name = 'browser/index-occurrence-word.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OccurrenceWordView, self).dispatch(*args, **kwargs)


class OccurrenceFamilyView(generic.DetailView):
    model = Family
    template_name = 'browser/index-occurrence-family.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OccurrenceFamilyView, self).dispatch(*args, **kwargs)


class FamiliesView(generic.TemplateView):
    template_name = 'browser/index-families.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FamiliesView, self).dispatch(*args, **kwargs)


class LetterView(generic.DetailView):
    model = Letter
    template_name = 'browser/detail.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LetterView, self).dispatch(*args, **kwargs)


class PeriodView(generic.TemplateView):
    template_name = 'browser/index-period.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PeriodView, self).dispatch(*args, **kwargs)


class FranciaView(generic.TemplateView):
    template_name = 'browser/index-francia.html'


class ModalLetterView(generic.DetailView):
    model = Letter
    template_name = 'browser/modal-letter.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ModalLetterView, self).dispatch(*args, **kwargs)


class ZipfView(generic.TemplateView):
    template_name = 'browser/zipflaw.html'
