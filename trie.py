from string_utils import get_text_suffixes
from auto_complete import AutoCompleteData

class TrieNode:
    """A node in the trie data structure"""

    def __init__(self, char):
        self.char = char
        self.is_end = False
        self.source_sentences = list()
        # a counter indicating how many times a word is inserted
        # (if this node's is_end is True)
        self.counter = 0
        # a dictionary of child nodes
        # keys are characters, values are nodes
        self.children = {}


class Trie(object):
    """The trie object"""

    def __init__(self):
        """
        The trie has at least the root node.
        The root node does not store any character
        """
        self.root = TrieNode("")

    def insert(self, text, path):
        """Insert a word into the trie"""

        suffixes = get_text_suffixes(text)
        for sentence in suffixes:
            node = self.root
            # Loop through each character in the word
            # Check if there is no child containing the character, create a new child for the current node
            for char in sentence:
                if char in node.children:
                    node = node.children[char]
                else:
                    # If a character is not found,
                    # create a new node in the trie
                    new_node = TrieNode(char)
                    node.children[char] = new_node
                    node = new_node
            # Mark the end of a word
            if sentence[len(sentence) - 1] == "\n":
                node.is_end = True
                node.source_sentences.append((text[:-1], path))
        # Increment the counter to indicate that we see this word once more
        node.counter += 1

    def dfs(self, node, prefix):
        """Depth-first traversal of the trie

        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if node.is_end:
            for text, path in node.source_sentences:
                offset = text.index(prefix)
                self.output.append(AutoCompleteData(text, path, offset, 1))
            # self.output.extend(node.source_sentences)

        for child in node.children.values():
            self.dfs(child, prefix + node.char)

    def query(self, x):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        self.output = []
        node = self.root

        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return []

        # Traverse the trie to get all candidates
        self.dfs(node, x[:-1])

        # Sort the results in reverse order and return
        return sorted(self.output, key=lambda x: x.offset)
