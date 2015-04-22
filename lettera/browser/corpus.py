from django.core.cache import cache
from django.core.urlresolvers import reverse
from collections import defaultdict, Counter
from browser.models import *
from math import factorial, log, exp, pi
import copy

class LFamily: 
  def __init__(self, pk, name) :
    self.pk = pk
    self.name = name

class LWord: 
  def __init__(self, pk, name, family) :
    self.pk = pk
    self.name = name
    self.family = family

class LOccurrence:
  def __init__(self, pk, word, family, sentence):
    self.pk = pk
    self.word = word
    self.family = family
    self.sentence = sentence

def load_corpus():

  families = dict()
  families_query = Family.objects.order_by('pk')
  for f in families_query:
    families[f.pk] = LFamily (f.pk, f.name)

  words = dict()
  words_query = Word.objects.order_by('pk')
  for w in words_query:
    words[w.pk] = LWord (w.pk, w.name, families[w.family_id])
  
  letters = defaultdict(list)
  occurrences_query = Occurrence.objects.order_by('pk')
  for o in occurrences_query:
    loc = LOccurrence(o.pk, words[o.word_id], families[o.family_id], o.sentence_id)
    letters[o.letter_id].append(loc)
  return [families, words, letters]

class Corpus :
  
  def __init__(self) : 
    datas = cache.get('corpus')
    if datas is None : 
      datas = load_corpus()
    cache.set('corpus', datas)
    [families, words, letters] = datas
    self.total = None
    self.families = families
    self.words = words
    self.letters = letters
    self.word_by_name = dict()
    self.words_by_family = defaultdict(set)
    for pk, word in words.items():
      self.word_by_name[word.name] = word
      self.words_by_family[word.family.pk].add(word)

    

  def search_word_letters(self, word):
    result = []
    for letter, text in self.letters.items() : 
      if word in (x.name for x in text) : 
        result.append(letter)
    return result

  def search_family_letters(self, family):
    result = []
    family_name = self.word_by_name[family].family.name
    for letter, text in self.letters.items() : 
      if family_name in (x.family.name for x in text) : 
        result.append(letter)
    return result

  def filter(self, filter_letters):
    result = copy.copy(self)
    result.letters = defaultdict()
    for key in self.letters : 
      if key in filter_letters:
        result.letters[key] = self.letters[key]
    return result

  def subcorpus(self, subcorpus_id) : 
    sc = Subcorpus.objects.get(pk=subcorpus_id)
    if sc.letters == '': 
      set_list = []
    else :
      set_list = set(map(int, sc.letters.split(',')))
    return self.filter(set_list)

  def subcorpus_statistics(self, subcorpus_id) : 
    if self.total is None :
      self.statistics() 
    subcorpus = self.subcorpus(subcorpus_id)
    result = subcorpus.statistics()

    def log_factorial(n) :
       if n <= 100:
         return log(factorial(n))
       return n*log(n) - n + log(n * ( 1 + 4*n*(1+2*n))) / 6 + log(pi) / 2


    def log_binom (n, p) : 
      return log_factorial(n) - log_factorial(n-p) - log_factorial(p)

    N = self.total
    n = subcorpus.total 

    assert (n <= N)

    CnN = log_binom(N, n)

    def avg(K):
      return float ((K * n) / N )

    def hyper (K, k): 
      l = log_binom(K, k) + log_binom(N - K, n - k) - CnN
      try:
        return exp(l)
      except OverflowError:
        print (N, n, K, k, l)
        return 0.0
    def test (K, k): 
      if k >= avg(K):
        step = 1
      else : 
        step = -1
      result = 0.0
      while True:
        increment = hyper(K, k)
        result += increment
        k += step
        if k < 0 or k > K or k < n - N + K or k > n or increment < 1e-20:
          break
      return step*result 

    for row in result['data']: 
      family_id = row['pk']
      K = self.occurrences[family_id]
      k = subcorpus.occurrences[family_id]
      row['hypertest'] = test(K, k)
      row['total_occurrences'] = K
      row['total_frequency'] = self.frequencies[family_id]
      row['relative_frequency'] = subcorpus.frequencies[family_id] / self.frequencies[family_id]
      
    return result

  def statistics(self):
    result = list()
    count = Counter()
    letters_from_word = defaultdict(Counter)
    occurring = set()
    letter_sizes = dict()
    for letter, text in self.letters.items() : 
      letter_sizes[letter] = len(text)
      for x in text : 
         occurring.add(x.family)
      for x in text:
        letters_from_word[x.family.pk][letter] += 1
      count.update(list(x.family.name for x in text))

    min_size = min(letter_sizes.values())

    occurring = list(occurring)
    occurring.sort(key=lambda x:x.pk)
    total = sum(count.values())
    N = len(self.letters)
    normalizer = 2.0 * (1.0 - float(min_size) / total)

    self.total = total
    self.sizes = dict()
    self.dispersions = dict()
    self.frequencies = dict()
    self.occurrences = dict()
    self.document_frequency = dict()
    
    for family in occurring:
      size = len(self.words_by_family[family.pk])
      occ = count[family.name]
      freq = float(occ) * 10000 / total
      letters = len(letters_from_word[family.pk])
      dispersion = 0.0
      for l in self.letters:
         dispersion += abs (float(letter_sizes[l]) / total - float(letters_from_word[family.pk][l]) / occ) 
      dispersion /= normalizer

      self.sizes[family.pk] = size
      self.dispersions[family.pk] = dispersion
      self.occurrences[family.pk] = occ
      self.document_frequency[family.pk] = letters
      self.frequencies[family.pk] = freq     

      result.append({ 'link' : reverse('occurrence-family', args=(family.pk,)),
                      'pk' : family.pk,
                      'name' : family.name, 
                      'frequency' : freq, 
                      'occurrences' : occ,
                      'letters' : letters,
                      'dispersion' : dispersion,
                      'size' : size })
    return { 'data' : result, 'leters' : N, 'total' : total } 
