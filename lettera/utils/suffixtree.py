import json

class smart_dict(dict):
  def __missing__(self, key):
    return (smart_dict(), 0) 

class SuffixTree():
  def __init__(self):
    self.root = smart_dict()

  def add(self, l):
    current = self.root
    for x in l:
      nxt, val  = current[x]
      val += 1
      current[x] = (nxt, val)
      current = nxt

  def json(self):
    def aux(root, name): 
      l = [ x for x in root.items() ]
      l.sort(key=lambda x:x[1][1], reverse=True)
      l = [ aux(r, x+' ({0})'.format(n)) for x, (r, n) in l ]
      return { 'name' : name, 'children' : l }

    return json.dumps(aux(self.root, "root"))

if False:
  test = SuffixTree()
  for x in ['bcd', 'cbd', 'bba', 'cdb', 'dcb', 'dbd']:
    test.add(x)
  print (test.root)
