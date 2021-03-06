from collections import deque
import os
from string_utils import clean_text


def process_input(dir_path, trie):
    """
    process and insert all data from a given directory and all of its sub-directories
    :param dir_path: directory path
    :param trie: trie object
    :return: None
    """

    if not os.path.isdir(dir_path):
        raise Exception("Invalid directory path")

    dirs = deque([dir_path])
    while len(dirs) > 0:
        curr_dir = dirs.popleft()
        curr_files = os.listdir(curr_dir)
        for file in curr_files:
            curr_path = f"{curr_dir}/{file}"
            if os.path.isdir(curr_path):
                dirs.append(curr_path)
                continue
            elif os.path.isfile(curr_path):
                insert_file_to_trie(curr_path, trie)
                print(f"Inserted {curr_path}")


def insert_file_to_trie(path, trie):
    """
    insert all file sentences (a line) into the trie data structure
    :param path: file path
    :param trie: trie object
    :return: None
    """

    with open(path, 'r+', encoding="utf8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            cleaned_line = clean_text(line)
            if len(cleaned_line) == 0:
                continue

            trie.insert(cleaned_line, path, idx)
