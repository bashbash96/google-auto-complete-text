import os
import pickle


def read_index(file_path):
    """
    read pickle file
    :param file_path: path of the pickle file
    :return: loaded file
    """
    if not os.path.isfile(file_path):
        raise Exception("Invalid file path")
    print("Loading the files and preparing the system...")
    with open(file_path, 'rb') as fid:
        return pickle.load(fid)
