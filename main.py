from preprocessing import process_input
from trie import Trie

t = Trie()
process_input('Input', t)
q = t.query('kah')
for res in q:
    print(res)
