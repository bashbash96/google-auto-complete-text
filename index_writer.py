import os
import pickle
from preprocessing import process_input
from trie import Trie


def write_index(dir_path):
    """
    write trie object into disk
    :param dir_path: path to load the data from
    :return: the save path
    """

    if not os.path.isdir(dir_path):
        raise Exception("Invalid directory path")

    trie = Trie()
    process_input(dir_path, trie)
    # save_path = 'result.pickle'
    # with open(save_path, 'wb') as fid:
    #     pickle.dump(trie, fid, protocol=pickle.HIGHEST_PROTOCOL)

    return trie
