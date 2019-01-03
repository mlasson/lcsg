import codecs
import re
import sys
import os
import secret

dir_path = os.path.dirname(os.path.realpath(__file__))
files = [os.path.join(dir_path, file) for file in ['ambassade.txt', 'gouverneur.txt']]

def read_letters():
    pattern = re.compile(r'(\d+)\.')
    cpt = 0
    result = []
    current = []
    for file in files:
        for line in open(file, 'r', encoding='utf-8'):
            line = line.rstrip().strip()
            m = pattern.match(line)
            if m is not None:
                n = int(m.group(1))
                cpt = cpt + 1
                if cpt != n:
                    raise Exception('Unable to parse letter {}'.format(n))
                if n > 1:
                    if not current:
                        raise Exception('Letter {} is empty'.format(n - 1))
                    result.append(u' '.join(current))
                    current = []
            else:
                current.append(line)
    return result

def main(force):
    result = []
    key = None
    for file in files:
        if not os.path.exists(file) or force:
            file_enc = file + '.encoded'
            if not os.path.exists(file_enc):
                raise Exception("Unable to find '{0}'".format(file_enc))
            if not key:
                key = secret.getkey()
            secret.decrypt_file(key, file_enc, file)

    letters = read_letters()
    for index, letter in enumerate(letters):
        output = u'''
  {{
      "pk" : null,
      "model" : "browser.letter",
      "fields" : {{
          "number" : {0}, 
          "volume" : {1},
          "period" : null, 
          "date" : null, 
          "text" : "{2}", 
          "author" : "Francesco Guicciardini"
      }}
  }}'''.format(index, 0, letter.replace('"', '\\"'))
        result.append(output)
    file = open(os.path.join(dir_path, "../fixtures/guichardin.json"), "w", encoding='utf-8') 
    file.write('[')
    file.write(','.join(result))
    file.write(']')
