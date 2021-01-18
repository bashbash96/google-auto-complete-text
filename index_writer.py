import os
from preprocessing import process_input
from trie import Trie

def write_index(dir_path):
    """

    :param dir_path:
    :return:
    """

    if not os.path.isdir(dir_path):
        raise Exception("Invalid directory path")

    trie = Trie()
    process_input('Input', trie)
    return trie
    #TODO: save trie as pickle file, return the path for the saved file..