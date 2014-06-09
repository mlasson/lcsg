#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import parsing, re, codecs
import re, codecs, logging

global_id = 0
global_id = 1

def first(n) : 
  table = [0,304,702,1085,1603,2168,2470]
  return table[n-1]

def parse_date(s):
  l = s.split('/')
  year = int(l[2])
  if year < 10 :
    year = '150'+str(year)
  elif year < 50 :
    year = '15'+str(year)
  else :
    year = '14'+str(year)
  month = l[1]
  day = l[0]
  return year+'-'+month+'-'+day

def roman(s) : 
  if s == "I" : 
    return 1 
  elif s == "II" : 
    return 2 
  elif s == "III" : 
    return 3
  elif s == "IV" :
    return 4
  elif s == "V" :
    return 5
  elif s == "VI" : 
    return 6 
  elif s == "VII" : 
    return 7
  elif s == "VIII" : 
    return 8
  print '#### wtf ??', s
  return 9

def escape(s):
  return s.replace('"', '\\"')

class Period :
  def __init__(self, start, end, name, volume, letters):
    global global_id 
    global_id = global_id + 1
    self.ident = global_id
    self.start = start
    self.end = end
    self.name = name
    self.volume = volume
    self.letters = letters

  def json(self):
    return u'''{{
    "pk" : {0.ident}, 
    "model" : "browser.period", 
    "fields" : {{
      "start" : "{0.start}", 
      "end" :"{0.end}", 
      "name" :"{0.name}"
    }}
  }}'''.format(self)

def fill_period_table():
  result = list()
  path = 'data/periods.csv'
  fd = codecs.open(path, 'r', 'utf-8')
  lines = fd.readlines()
  for line in lines : 
    line = line[0:-1] 
    infos = line.split(',')
    l = infos[6].split(' ')
    volume = roman(l[0])
    r = l[1].split('-')
    if len(r) == 2:
      ran = range(int(r[0]),int(r[1])+1)
    elif len(r) == 1 :
      ran = [int(r[0])]
    else : 
      raise Exception('Strange range :'+l[1])
    ran = [ first(volume) + x - 1 for x in ran ]
    start = infos[0]
    if len(infos[1]) > 0:
      end = infos[1]
    else : 
      end = start
    name = infos[2]
    total = int(infos[3])
    result.append(Period(parse_date(start), parse_date(end), name, volume, ran))
  return result

class Words():
  def __init__(self) : 
    self.words = set()
    self.families = list()
    self.family = dict()
    path = 'data/merge_file.txt'
    fd = codecs.open(path, 'r', 'utf-8')
    lines = fd.readlines()
    for line in lines : 
      line = re.sub(':','',line)
      ws = line.split()
      if len(ws) < 1:
	logging.warning('empty line in merge_file')
	continue
      if ws[0] in self.families:
	logging.warning('try to register a family twice:'+ws[0])
      self.families.append(ws[0])
      for w in ws : 
	self.words.add(w)
	if w in self.family and self.family[w] != ws[0]: 
	  logging.warning('multiple occurrence of '+w+' for '+ws[0])
	self.family[w]=ws[0]

  def json(self):
    result = []
    for x in range(len(self.families)):
      result.append(u'''{{
  "pk" : {0}, 
  "model" : "browser.family", 
  "fields" : {{
    "name" : "{1}" 
  }}
}}'''.format(x, self.families[x]))
    ident = 0
    for w in self.words:
      ident = ident + 1
      result.append(u'''{{
  "pk" : {0}, 
  "model" : "browser.word", 
  "fields" : {{
    "name" : "{1}", 
    "family" : "{2}" 
  }}
}}'''.format(ident, w,self.families.index(self.family[w])))
    return result



class Lettera :
  def __init__(self, number, volume, title, text, comment) : 
    global global_id
    self.ident = global_id
    self.number = number
    self.volume = roman(volume)
    self.title = title
    self.author = u'Niccolò Machiavelli'
    self.day = None
    self.month = None
    self.year = None
    self.date = None
    self.ignore = None
    self.note = None
    self.period_id = None
    if title : 
      self.text = title + text
    else :
      self.text = text
    self.comment = comment
    global_id = global_id + 1

  def json(self) :
    date = self.date
    if not self.date :
      date = 'null'
    else :
      date = '"'+date+'"'
    period = 'null'
    if self.period_id : 
      period = self.period_id
    return u'''{{
  "pk" : {0.ident}, 
  "model" : "browser.letter", 
  "fields" : {{
    "number" : {0.number}, 
    "volume" : {0.volume}, 
    "period" : {3}, 
    "date" : {1},
    "text" : "{2}",
    "author" : "{0.author}"
  }}
}}'''.format(self, date, escape(self.text), period)

  def update_info(self, infos) : 
    if not (infos[1] == '??') : 
       self.day = infos[1] 
    if not (infos[2] == '??') : 
       self.month = infos[2] 
    if not (infos[3] == '????') : 
       self.year = infos[3] 
    self.note = infos[4]
    if not (infos[3] == '????') and not (infos[2] == '??') :
      self.date = infos[3]+'-'+infos[2]
    if not (infos[3] == '????') and not (infos[2] == '??') and not (infos[1] == '??'):
      self.date = infos[3]+'-'+infos[2]+'-'+infos[1].split('-')[0]
    if re.search ("à M", self.note) or re.search ("sur M", self.note) or re.search ("ignore", self.note) : 
      self.ignore = 'true'
    # print self.volume, self.number, infos[1], infos[2], infos[3], self.date

def parsing_letter_number (s) : 
  number_pattern = re.compile (r'(\d+)')
  res = number_pattern.findall(s)
  if len(res) <> 1 :
    print 'Erreur : numéro de lettre étrange "', s, '"'
    exit
  return int(res[0])


if __name__ == "__main__" :
  path = '../lettera/fixture/'
  corpis = [ "LCSG/LCSG I.html", "LCSG/LCSG II.html", "LCSG/LCSG III.html", "LCSG/LCSG IV.html", "LCSG/LCSG V.html", "LCSG/LCSG VI.html", "LCSG/LCSG VII.html" ]
  corpus_name = ["I","II", "III", "IV", "V", "VI", "VII"]
  database = list()

  # fill periods :
  periods = fill_period_table()

  for i in xrange(0,len(corpis)) : 
    print '-- Traitement du volume', corpus_name[i]
    output = parsing.parse_file("data/"+corpis[i])
    for num, title, text, comment in output : 
      lettera = Lettera(parsing_letter_number(num), corpus_name[i], title, text, comment)
      for p in periods : 
	if p.volume == lettera.volume and lettera.number in p.letters:
	  if lettera.period_id :
	    logging.warning('the letter {0} in the volume {1} already in period {2}'.format(lettera.number, lettera.volume, lettera.ident))
          lettera.period_id = p.ident
      database.append(lettera)

  print '-- Ajout des informations ...'
  for k in range(1, 8) : 
    filename = 'data/infos/DATES VOL '+str(k)+'.txt'
    f = open(filename, 'r')
    # pat = re.compile(r'(\d+)\s+(\d+)\s+((?:\w|-)+)/((?:\w|-)+)/((?:\w|-)+)\s+([^\n]*)\n?$')
    pat = re.compile(r'(\d+)\s+((?:\d|-|\?)+)/((?:\d|-|\?)+)/((?:\d|-|\?)+)\s+([^\n]*)\n?$')
    infos = dict()
    for line in f.readlines(): 
      m = pat.match(line)
      if m : 
	r = m.groups()
	infos[r[0]] = r
    for l in database:
      if l.volume == k and str(l.number) in infos: 
	l.update_info(infos[str(l.number)])


  words = Words()
  # all outputs : 
  # outputs letter :
  output_name = 'datas.json'
  output_file = codecs.open(path + output_name, "w", "utf-8")
  periods_jsoned = [ l.json() for l in periods]
  output_file.write('['+',\n'.join(periods_jsoned)+',')
  not_ignored = [l for l in database if not l.ignore]
  letter_list_jsoned = [ l.json() for l in database if not l.ignore]
  logging.warning('not_ignored = {0}, full = {1}, diff = {2}'.format(len(not_ignored), len(database), len(database) - len(not_ignored)))
  output_file.write(',\n'.join(letter_list_jsoned)+',')
  words_jsoned = words.json()
  output_file.write(',\n'.join(words_jsoned)+']')



