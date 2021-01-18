import os
from trie import Trie


def read_index(file_path):
    """

    :param file_path:
    :return:
    """
    if not os.path.isfile(file_path):
        raise Exception("Invalid file path")
    return
