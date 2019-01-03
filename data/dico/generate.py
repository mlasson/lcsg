import sys
import os
import secret

class Reader():
    def __init__(self, dico_file):
        self.all_words = set()
        self.family = dict()
        self.all_titles = set()
        self.ids = dict()
        self.dico_file = dico_file

        self.parse_dico()

    def save(self, json_file):
        stream = []
        output = open(json_file, "w", encoding='utf-8')
        for id, title in enumerate(self.all_titles):
            self.ids[title] = id
            self.output_title(id, title, stream)

        for id, word in enumerate(self.all_words):
            self.output_word(id, word, stream)

        output.write('[')
        output.write(','.join(stream))
        output.write(']')

    def parse_entry(self, title, words):
        title = title.strip()
        words = words.split()
        line_set = set()
        if title in self.all_titles:
            print("Title '{0}' occuring twice".format(title))
        else:
            self.all_titles.add(title)
        for word in words:
            word = word.strip()
            if word in line_set: 
                print("Local duplicated detected '{0}'".format(word))
            else:
                line_set.add(word)
                if word not in self.family:
                    self.family[word] = title
                if word not in self.all_words:         
                    self.all_words.add(word)
                elif word in self.family:
                    print("Possible merge of '{1}' with family '{0}'".format(self.family[word], word))
                else:
                    print("Global duplicate detected '{0}'".format(word))
        if title not in words :
            print("Missing title '{0}' in words".format(title))
            # line_set.add(title)

    def parse_dico(self):
        line_number = 0
        for line in open(self.dico_file, 'r', encoding='utf-8'):
            line_number = line_number + 1
            line = line.rstrip().replace(',', ' ').strip()
            entry = line.split(':')
            if len(entry) != 2: 
                print('Cannot parse entry {1} : \'{0}\''.format(line, line_number))
            else:             
                self.parse_entry(entry[0], entry[1])

    def output_title(self, id, title, stream):
        if title == 'IGNORED': 
            title = 'IGNORED WORDS'
        stream.append(u'''
    {{
        "pk" : {0},
        "model" : "browser.family",
        "fields" : {{
            "name" : "{1}"
        }}
    }}'''.format(id, title))

    def output_word(self, id, word, stream):
        family_id = self.ids[self.family[word]]
        stream.append(u'''
    {{
        "pk" : "{0}",
        "model" : "browser.word",
        "fields" : {{
            "name" : "{1}", 
            "family" : "{2}"
        }}
    }}'''.format(id, word, family_id))

def main(force):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dico_file = os.path.join(dir_path, "dico.txt")
    json_file = os.path.join(dir_path, "../fixtures/dico.json")
    if not os.path.exists(dico_file) or force:
        file_enc = dico_file + '.encoded'
        if not os.path.exists(file_enc):
            raise Exception("Unable to find '{0}'".format(file_enc))
        secret.decrypt_file(secret.getkey(), file_enc, dico_file)
    reader = Reader(dico_file)
    reader.save(json_file)
