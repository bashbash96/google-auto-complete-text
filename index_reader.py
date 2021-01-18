import os
import pickle
from trie import Trie


def read_index(file_path):
    """

    :param file_path:
    :return:
    """
    if not os.path.isfile(file_path):
        raise Exception("Invalid file path")
    print("Loading the files and preparing the system...")
    with open(file_path, 'rb') as fid:
        return pickle.load(fid)
