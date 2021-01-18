import numpy as np
from string_utils import get_text_suffixes, get_text_from_path, clean_text
from auto_complete import AutoCompleteData

SUB_SCORE = 1
REMOVE_SCORE = 2
LAST_CHAR_SCORE = 5


class TrieNode:
    """A node in the trie data structure"""

    def __init__(self, char):
        self.char = char
        self.source_sentences = list()
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

    def insert(self, text, path, line_idx):
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
            node.source_sentences.append((line_idx, path))

    def get_full_match(self, text, k):
        self.output = []
        self.visited = set()
        node = self.root

        # Check if the prefix is in the trie
        for char in text:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return []

        # Traverse the trie to get all candidates
        self.dfs(node, text[:-1], len(text), 0, k)

    @staticmethod
    def get_score(idx, type):
        """

        :param idx:
        :param type: 1- substitution, 2- remove
        :return:
        """

        if idx >= (LAST_CHAR_SCORE - 1):
            return type

        return type * (LAST_CHAR_SCORE - idx)

    def get_substitution_match(self, text, node, k, idx=0, sub_idx=-1, spelling_err=0):
        """

        :param text:
        :return:
        """

        if spelling_err > 1 or len(self.output) >= k:
            return

        if idx >= len(text):
            if sub_idx < 0:
                return
            original_len = len(text)
            if sub_idx != len(text):
                original_len -= 1
            self.dfs(node, text[:-1], original_len, self.get_score(sub_idx, SUB_SCORE), k)
            return

        if text[idx] in node.children:
            self.get_substitution_match(text, node.children[text[idx]], k, idx + 1, sub_idx, spelling_err)
            if len(self.output) >= k:
                return
            for char in node.children:
                if char != text[idx]:
                    spelling_err += 1
                    self.get_substitution_match(text[:idx] + char + text[idx + 1:], node.children[char], k, idx + 1,
                                                idx, spelling_err)
                    spelling_err -= 1
        else:
            spelling_err += 1
            if idx == len(text) - 1:
                self.get_substitution_match(text[:-1], node, k, idx + 1, idx, spelling_err)
                return
            else:
                for char in node.children:
                    curr_ndoe = node.children[char]
                    if text[idx + 1] in curr_ndoe.children:
                        self.get_substitution_match(text[:idx] + char + text[idx + 1:], curr_ndoe, k, idx + 1, idx,
                                                    spelling_err)

    def get_remove_match(self, text, node, k, idx=0, rem_idx=-1, spelling_err=0):
        """

        :param text:
        :return:
        """

        if spelling_err > 1 or len(self.output) >= k:
            return

        if idx >= len(text):
            if rem_idx < 0:
                return
            self.dfs(node, text[:-1], len(text), self.get_score(rem_idx, REMOVE_SCORE), k)
            return

        if text[idx] in node.children:
            self.get_remove_match(text, node.children[text[idx]], k, idx + 1, rem_idx, spelling_err)
            if len(self.output) >= k:
                return
            for char in node.children:
                if spelling_err > 0:
                    break
                spelling_err += 1
                self.get_remove_match(text[:idx] + text[idx + 1:], node.children[char], k, idx,
                                      idx, spelling_err)
                spelling_err -= 1
        else:
            spelling_err += 1
            if idx == len(text) - 1:
                self.get_remove_match(text[:-1], node, k, idx + 1, idx, spelling_err)
                return
            else:
                if text[idx + 1] in node.children:
                    self.get_remove_match(text[:idx] + text[idx + 1:], node, k, idx, idx,
                                          spelling_err)

    def get_add_match(self, text, node, k, idx=0, add_idx=-1, spelling_err=0):
        """

        :param text:
        :return:
        """

        if spelling_err > 1 or len(self.output) >= k:
            return

        if idx >= len(text):
            if add_idx < 0:
                return
            original_len = len(text)
            if add_idx != len(text):
                original_len -= 1
            self.dfs(node, text[:-1], original_len, self.get_score(add_idx, REMOVE_SCORE), k)
            return

        if text[idx] in node.children:
            self.get_add_match(text, node.children[text[idx]], k, idx + 1, add_idx, spelling_err)
            if len(self.output) >= k:
                return
            for char in node.children:
                spelling_err += 1
                self.get_add_match(text[:idx] + char + text[idx:], node.children[char], k, idx + 1,
                                   idx, spelling_err)
                spelling_err -= 1
        else:
            spelling_err += 1
            for char in node.children:
                curr_ndoe = node.children[char]
                if text[idx] in curr_ndoe.children:
                    self.get_add_match(text[:idx] + char + text[idx:], curr_ndoe, k, idx + 1, idx,
                                       spelling_err)

    def dfs(self, node, prefix, original_len, error_score, k):
        """Depth-first traversal of the trie

        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if len(self.output) >= k:
            return

        if len(node.source_sentences) > 0:
            for line_idx, path in node.source_sentences:
                text = get_text_from_path(path, line_idx)
                cleaned_text = clean_text(text)
                try:
                    offset = cleaned_text.index(prefix)
                except Exception as e:
                    continue
                if (line_idx, path) in self.visited:
                    return
                self.output.append(AutoCompleteData(text, path, offset, (original_len * 2) - error_score))
                self.visited.add((line_idx, path))

        for child in node.children.values():
            self.dfs(child, prefix + node.char, original_len, error_score, k)

    def get_best_k_completions(self, text, k=5):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix

        # Sort the results in reverse order and return

        self.get_full_match(text, k)
        self.get_substitution_match(text, self.root, k)
        self.get_remove_match(text, self.root, k)
        self.get_add_match(text, self.root, k)
        return sorted(self.output, key=lambda x: (-x.score, x.completed_sentence))[:k]
