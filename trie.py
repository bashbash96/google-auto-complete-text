from string_utils import get_text_suffixes, get_text_from_path, clean_text
from auto_complete import AutoCompleteData

# Constants
SUB_SCORE = 1
REMOVE_SCORE = 2
LAST_CHAR_SCORE = 5


class TrieNode:
    """
    A node in the trie data structure
    """

    def __init__(self, char):
        # the char that the node is holding
        self.char = char
        # all the sentences that this char end with
        self.source_sentences = list()
        # a dictionary of child nodes
        # keys are characters, values are nodes
        self.children = {}


class Trie(object):
    """
    The trie object
    """

    def __init__(self):
        """
        The trie has at least the root node.
        The root node does not store any character
        """
        self.root = TrieNode("")
        self.output = []
        self.visited = set()

    def insert(self, text, path, line_idx):
        """
        Insert a word into the trie
        :param text: the full line
        :param path: path of the source file for the current line
        :param line_idx: the index of the current line in the relevant file
        :return: None
        """

        suffixes = get_text_suffixes(text)
        for sentence in suffixes:
            node = self.root
            # go through each character in the word
            # Check if there is no child containing the character,
            # if so create a new child for the current node
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

        # # optimization for the memory, instead of saving all the suffixes
        # # save only the sentence itself and after each space put a pointer
        # # from the root to the current node in order to get the relevant suffix
        # prev_char = ''
        # node = self.root
        # for char in text:
        #     node = node.children[char]
        #     if prev_char == ' ':
        #         self.root.children[char] = node
        #     prev_char = char

    def get_full_match(self, text, k):
        """
        search for all full matches to the given text, save it in output
        :param text: the user text
        :param k: most k appropriated
        :return: k top scores matches
        """

        # when start new search, empty the result
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
        get score to specific correction by its type

        :param idx: the index of the spelling error
        :param type: 1- substitution, 2- removal/addition
        :return: the relevant score
        """

        # if the index is after the fourth one, then its according to type
        if idx >= (LAST_CHAR_SCORE - 1):
            return type

        # the score has opposite correlation with the index of the error
        return type * (LAST_CHAR_SCORE - idx)

    def get_substitution_match(self, text, node, k, idx=0, sub_idx=-1, spelling_err=0):
        """
        search for all one substitution matches, save it in output
        if it found top 5 matches, return
        :param text: the original text
        :param node: the current node in the trie object
        :param k: top k score matches
        :param idx: current index in the original text
        :param sub_idx: the index of the substitution on the original text
        :param spelling_err: how many errors tell now
        :return:
        """

        if spelling_err > 1 or len(self.output) >= k:
            return

        # if we found a valid match with one correction, get all its completions
        if idx >= len(text):
            if sub_idx < 0:
                return
            original_len = len(text)
            if sub_idx != len(text):
                original_len -= 1
            self.dfs(node, text[:-1], original_len, self.get_score(sub_idx, SUB_SCORE), k)
            return

        # get the most appropriate match for the current text
        if text[idx] in node.children:
            self.get_substitution_match(text, node.children[text[idx]], k, idx + 1, sub_idx, spelling_err)
            if len(self.output) >= k:
                return
            # if it finished all the matches and still need more results,
            # try to substitute valid chars by backtracking
            for char in node.children:
                if char != text[idx]:
                    spelling_err += 1
                    self.get_substitution_match(text[:idx] + char + text[idx + 1:], node.children[char], k, idx + 1,
                                                idx, spelling_err)
                    spelling_err -= 1
        else:
            # if there is a missing char, check for appropriate
            # char from the trie to replace it. check if the next char in original text
            # is a child of the candidate char from the trie in order not to get two spelling errors
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
        search for all one remove matches, save it in output
        if it found top 5 matches, return
        :param text: the original text
        :param node: the current node in the trie object
        :param k: top k score matches
        :param idx: current index in the original text
        :param rem_idx: the index of the removed char on the original text
        :param spelling_err: how many errors tell now
        :return:
        """

        if spelling_err > 1 or len(self.output) >= k:
            return

        # if we found a valid match with one correction, get all its completions
        if idx >= len(text):
            if rem_idx < 0:
                return
            self.dfs(node, text[:-1], len(text), self.get_score(rem_idx, REMOVE_SCORE), k)
            return

        # get the most appropriate match for the current text
        if text[idx] in node.children:
            self.get_remove_match(text, node.children[text[idx]], k, idx + 1, rem_idx, spelling_err)
            if len(self.output) >= k:
                return

            # if it finished all the matches and still need more results,
            # try to remove valid chars by backtracking
            for char in node.children:
                if spelling_err > 0:
                    break
                spelling_err += 1
                self.get_remove_match(text[:idx] + text[idx + 1:], node.children[char], k, idx,
                                      idx, spelling_err)
                spelling_err -= 1
        else:
            # if there is a missing char, try to remove appropriate
            # char from the text. check if the next char in the original text
            # is a child of the current node from the trie in order not to get two spelling errors
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
        search for all one add matches, save it in output
        if it found top 5 matches, return
        :param text: the original text
        :param node: the current node in the trie object
        :param k: top k score matches
        :param idx: current index in the original text
        :param add_idx: the index of the added char on the original text
        :param spelling_err: how many errors tell now
        :return:
        """

        if spelling_err > 1 or len(self.output) >= k:
            return

        # if we found a valid match with one correction, get all its completions
        if idx >= len(text):
            if add_idx < 0:
                return
            original_len = len(text)
            if add_idx != len(text):
                original_len -= 1
            self.dfs(node, text[:-1], original_len, self.get_score(add_idx, REMOVE_SCORE), k)
            return

        # get the most appropriate match for the current text
        if text[idx] in node.children:
            self.get_add_match(text, node.children[text[idx]], k, idx + 1, add_idx, spelling_err)
            if len(self.output) >= k:
                return

            # if it finished all the matches and still need more results,
            # try to add valid chars from the trie by backtracking
            for char in node.children:
                spelling_err += 1
                self.get_add_match(text[:idx] + char + text[idx:], node.children[char], k, idx + 1,
                                   idx, spelling_err)
                spelling_err -= 1
        else:
            # if there is a missing char, try to add appropriate char from the trie to the text
            # and check if the missing char in the original text
            # is a child of the added char node from the trie in order not to get two spelling errors
            spelling_err += 1
            for char in node.children:
                curr_ndoe = node.children[char]
                if text[idx] in curr_ndoe.children:
                    self.get_add_match(text[:idx] + char + text[idx:], curr_ndoe, k, idx + 1, idx,
                                       spelling_err)

    def dfs(self, node, prefix, original_len, error_score, k):
        """
        Depth-first traversal of the trie
        :param node: current node
        :param prefix: current prefix for tracking word while traversing
        :param original_len: the original text length (without addition, substitution, removal)
        :param error_score: the spelling error correction score (if there is no error the score is 0)
        :param k: top k matches
        :return:
        """

        if len(self.output) >= k:
            return

        # if there is at least one sentence that ends with this node take it
        if len(node.source_sentences) > 0:
            for line_idx, path in node.source_sentences:
                # get the text from the file by its index and file path
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

        # traverse all children of the current node
        for child in node.children.values():
            self.dfs(child, prefix + node.char, original_len, error_score, k)

    def get_best_k_completions(self, text, k=5):
        """
        Given an input (a prefix), retrieve all sentences stored in
        the trie with that prefix, or that has a Levenshtein distance of 1 from
        the original text, and sort them according to score.
        :param text: user input
        :param k: top k scores
        :return: top k results
        """

        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        # Sort the results in reverse order and return

        self.get_full_match(text, k)
        self.get_substitution_match(text, self.root, k)
        self.get_remove_match(text, self.root, k)
        self.get_add_match(text, self.root, k)
        return sorted(self.output, key=lambda x: (-x.score, x.completed_sentence))[:k]
