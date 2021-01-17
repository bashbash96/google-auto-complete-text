from preprocessing import process_input
from basic_trie import Trie

# string1 = "how to sleep 10 hours\n"
# string2 = "how to eat burger\n"
# string3 = "I love programming\n"
# prefixes1 = all_prefixes(string1)
# prefixes2 = all_prefixes(string2)
# prefixes3 = all_prefixes(string3)

t = Trie()
process_input('Input', t)
print(t.query('goo'))
# for prefix in prefixes1:
#     t.insert(prefix)
#
# for prefix in prefixes2:
#     t.insert(prefix)
#
# for prefix in prefixes3:
#     t.insert(prefix)

print(t.query("I lov"))  # --> "I"