import sys

if len(sys.argv) != 3:
    print ('usage: clean.py <input> <output>')
    exit(1)

dico_file = sys.argv[1]
normalize_file = sys.argv[2]
all_words = set()

family = dict()

output = open(normalize_file, "w", encoding='utf-8')

def parse_entry(title, words):
    title = title.strip()
    words = words.split()
    line_set = set()
    for word in words:
        word = word.strip()
        if word in line_set: 
            print("Local duplicated detected '{0}'".format(word))
        else:
            line_set.add(word)
            if word not in family:
                family[word] = title
            if word not in all_words:         
                all_words.add(word)
            elif word in family:
                print("Possible merge of '{1}' with family '{0}'".format(family[word], word))
            else:
                print("Global duplicate detected '{0}'".format(word))
    if title not in words and title != "NUMERALS" and title != "LATIN": 
        print ("Missing title '{0}' in words".format(title))
        line_set.add(title)
    output.write('{0} : {1}\n'.format(title, ' '.join(line_set)))

def parse_dico():
    line_number = 0
    for line in open(dico_file, 'r', encoding='utf-8'):
        line_number = line_number + 1
        line = line.rstrip().replace(',', ' ').strip()
        entry = line.split(':')
        if len(entry) != 2: 
            print('Cannot parse entry {1} : \'{0}\''.format(line, line_number))
        else:             
            parse_entry(entry[0], entry[1])


parse_dico()
output.close()