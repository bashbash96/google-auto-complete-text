import numpy as np
from string_utils import get_text_suffixes
from auto_complete import AutoCompleteData

SUB_SCORE = 1
REMOVE_SCORE = 2
LAST_CHAR_SCORE = 5

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

    def get_full_match(self, text):
        self.output = []
        node = self.root

        # Check if the prefix is in the trie
        for char in text:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return []

        # Traverse the trie to get all candidates
        self.dfs(node, text[:-1], len(text), 0)

    def get_score(self, idx, type):
        """

        :param idx:
        :param type: 1- substitution, 2- remove
        :return:
        """
        if idx >= (LAST_CHAR_SCORE - 1):
            return type
        return type * (LAST_CHAR_SCORE - idx)

    def get_substitution_match(self, text, node, idx=0, sub_idx=-1, spelling_err=0):
        """

        :param text:
        :return:
        """
        if spelling_err > 1 or len(self.output) >= 5:
            return

        while idx < len(text):
            if text[idx] in node.children:
                node = node.children[text[idx]]
            else:
                spelling_err += 1
                if idx == len(text) - 1:
                    self.get_substitution_match(text[:-1], node, idx + 1, idx, spelling_err)
                    return
                else:
                    for char in node.children:
                        curr_ndoe = node.children[char]
                        if text[idx + 1] in curr_ndoe.children:
                            self.get_substitution_match(text[:idx] + char + text[idx + 1:], curr_ndoe, idx + 1, idx,
                                                        spelling_err)
            idx += 1

        if sub_idx < 0:
            return

        self.dfs(node, text[:-1], len(text), self.get_score(sub_idx, SUB_SCORE))

    def get_remove_match(self, text, node, idx=0, rem_idx=-1, spelling_err=0):
        """

        :param text:
        :return:
        """
        if spelling_err > 1 or len(self.output) >= 5:
            return

        while idx < len(text):
            if text[idx] in node.children:
                node = node.children[text[idx]]
            else:
                spelling_err += 1
                if idx == len(text) - 1:
                    self.get_substitution_match(text[:-1], node, idx + 1, idx, spelling_err)
                    return
                else:
                    self.get_substitution_match(text[:idx] + text[idx + 1:], node, idx + 1, idx,
                                                spelling_err)
            idx += 1

        if rem_idx < 0:
            return
        self.dfs(node, text[:-1], len(text), self.get_score(rem_idx, REMOVE_SCORE))

    def dfs(self, node, prefix, original_len, error_score):
        """Depth-first traversal of the trie

        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if len(self.output) >= 5:
            return

        if node.is_end:
            for text, path in node.source_sentences:
                try:
                    offset = text.index(prefix)
                except Exception as e:
                    continue
                self.output.append(AutoCompleteData(text, path, offset, (original_len * 2) - error_score))

        for child in node.children.values():
            self.dfs(child, prefix + node.char, original_len, error_score)

    def query(self, text):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix

        # Sort the results in reverse order and return
        self.get_full_match(text)
        self.get_substitution_match(text, self.root)
        self.get_remove_match(text, self.root)
        return sorted(self.output, key=lambda x: (-x.score, x.completed_sentence))
