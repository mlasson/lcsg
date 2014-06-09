#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import re, sys, textwrap, codecs
import lxml.etree as etree

def xhtml_tag(s):
  return '{http://www.w3.org/1999/xhtml}'+s


header = re.compile(ur'(?:.*[^\[\d])?(\d+)')
header_weak = re.compile(ur'(\d+)\.')
header_comment = re.compile(ur'^\d+\.')
header_comment_weak = re.compile(ur'[^\d\[]?(\d+)([^\d\]]|$)')
break_line = re.compile(ur'^(\s| )*$')
start = re.compile(ur'^(\s| )*\[\d')

debug = False

class Parser : 

  def reset(self, next_number):
    try :
      number = int(next_number)
    except ValueError :
      print 'Erreur de nombre :', next_number
      number = -1
    if number == self.number_theory :
      self.current = []
      self.current_title = []
      self.current_comment = []
      self.current_number = next_number
      self.parse_number = True
      self.parse_title = False
      self.parse_text = False
      self.parse_comment = False
      self.number_theory += 1
    elif debug : 
      print 'Reset not allowed'

  def full_reset(self) : 
    self.reset ('0')
    self.output = []

  def __init__(self, tree) : 
    self.root = tree.getroot()
    self.body = self.root.findall(xhtml_tag('body'))
    self.paragraph = False
    self.number_theory = 0
    self.full_reset()

  def stack(self):
    title = ' '.join(self.current_title)
    title = ' '.join(title.split())
    text = ' '.join(self.current)
    text = ' '.join(text.split())
    comment = ' '.join(self.current_comment)
    comment = ' '.join(comment.split())

    if len(text) < 250 or len(title) > 300 : 
      text = title + text
      title = None
    if (len (text) < 100 or len(comment) < 15) and self.current_number <> '0'  : 
      print 'Lettre suspecte : ', self.current_number.encode('utf-8')

    self.output.append((self.current_number, title, text, comment))


  def print_state(self):
    print 'State (curent number', self.current_number, '): ',
    if self.parse_number : 
      print 'parse number'
    if self.parse_text :
      print 'parse text'
    if self.parse_title :
      print 'parse title'
    if self.parse_comment :
      print 'parse comment'
 
  def append_text(self, s):
    if debug : 
       print 'append "', ' '.join(s.split()).encode('utf-8'), '" in ... '
       self.print_state()
    if self.parse_text:
      self.current.append(s)
    if self.parse_title :
      self.current_title.append(s)
    if self.parse_comment :
      self.current_comment.append(s)

  def change_state (self, has_children, text) : 
    if debug: 
      print 'We should look in this tag ...'
      print 'has children', has_children
      print 'Text \''+text.encode('utf-8')+'\''
    if self.paragraph and not has_children :
      if debug : 
        print 'We\'re in a paragraph childless'
      match_header = header.match(text)
      if match_header:
	value = match_header.group(1)
	if debug : 
	  print "Matched number :", value
	if value == self.current_number and self.parse_text : 
	  self.parse_text = False
	  self.parse_comment = True
	elif int(value) == self.number_theory :
	  self.stack()
	  self.reset(value)
	elif debug : 
	  print 'Mismatch ', int(value), ' with ', self.number_theory
      elif debug : 
        print 'Not a number ! \'', text.encode('utf-8'), '\''
    else :
      match_header = header_weak.match(text)
      if match_header:
	value = match_header.group(1)
	if debug : 
	  print "Matched number :", value
	if value == self.current_number and self.parse_text : 
	  self.parse_text = False
	  self.parse_comment = True
	elif int(value) == (self.number_theory) :
	  self.stack()
	  self.reset(value)
	elif debug : 
	  print 'Mismatch ', int(value), ' with ', self.number_theory
      elif debug : 
        print 'Not a number ! \'', text.encode('utf-8'), '\''


    if self.parse_text or self.parse_title :
      if debug: 
	print 'Do we change state ?'
      match_header_comment = header_comment.match(text)
      if match_header_comment :
	self.parse_text = False
	self.parse_comment = True
      else :
	if debug: 
	  print 'Try to catch a number ...'
	smooth_text = ' '.join(text.split())
	match_header_comment_weak = header_comment_weak.match(smooth_text)
	if match_header_comment_weak:
	  n = match_header_comment_weak.group(1) 
	  if debug : 
	    print 'Nombre testé : ', n
	  if n == self.current_number:
	    print 'Commentaire chopé :'+self.current_number, text.encode('utf-8')
	    self.parse_text = False
	    self.parse_comment = True
	elif debug : 
	  print 'fail with \''+text.encode('utf-8')+'\''

    if self.parse_number : 
      match_start = start.match(text)
      if match_start : 
	if debug : 
	  print 'start :', text.encode('utf-8')
	self.parse_title = True
	self.parse_number = False

    if self.parse_title and self.paragraph and not has_children:
      match_break_line = break_line.match(text)
      if match_break_line :
	if debug : 
	  print 'break_line :', text.encode('utf-8')
	self.parse_title = False
	self.parse_text = True


  def show_node(self, node):
    if debug : 
      print '---> ', node
      if node.text: 
	print 'text :"', ' '.join(node.text.split()).encode('utf-8'), '"'
      if node.tail: 
	print 'tail :"', ' '.join(node.tail.split()).encode('utf-8'), '"'
      self.print_state()
    
    show_text = False
    if node.tag == xhtml_tag('p') : 
      show_text = True
      self.paragraph = True
    else :
      self.paragraph = False
    if node.tag == xhtml_tag('span') : 
      show_text = True
    if node.tag == xhtml_tag('div') : 
      show_text = True

    if show_text and node.text <> None :
      self.change_state(list(node)<>[], node.text)
      self.append_text(node.text)

    for child in node:
      self.show_node(child)
      if child.tail <> None : # J'AI VIRÉ le test à show_text
	self.change_state(True, child.tail)
	self.append_text(child.tail)
    if debug : 
      print '<--- ', node
   
  def parse(self) : 
    self.show_node(self.body[0])
    self.stack() 
    res = self.output
    self.full_reset()
    return res[1:]

def parse_file(name) : 
  input_file = codecs.open(name, encoding='utf-8')
  tree = etree.parse(input_file)
  parser = Parser(tree)
  output = parser.parse()
  return output

if __name__ == "__main__":
  output = parse_file(sys.argv[1])
  debug = len(sys.argv) == 3

  print_letter = False
  print_title = False
  print_comment = False
  num_theo = 0
  for num, title, text, comment in output : 
    num_theo += 1
    print 'Lettera ', num.encode('utf-8')
    if str(num_theo) != num : 
      print 'Error theorical number =', num_theo, ' instead ', num
    if print_title and title : 
      out = title
      print '    ', out.encode('utf-8')
    if print_letter:
      print '──────────────────────────────────────────────────────────────────────' 
      out = text
      out = textwrap.fill(out, expand_tabs=False,drop_whitespace=False,fix_sentence_endings=True)
      print out.encode('utf-8')
      print '──────────────────────────────────────────────────────────────────────' 

    if print_comment:
      print 'Comment : '
      print '──────────────────────────────────────────────────────────────────────' 
      out = comment
      out = textwrap.fill(out, expand_tabs=False,drop_whitespace=False,fix_sentence_endings=True)
      print out.encode('utf-8')
      print '──────────────────────────────────────────────────────────────────────' 

    print ''
