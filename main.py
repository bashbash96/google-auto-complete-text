from preprocessing import process_input
from trie import Trie
import argparse

t = Trie()
process_input('Input', t)
q = t.query("kir")
for res in q:
    print(res)

def main(*args, **kwargs):
    pass
