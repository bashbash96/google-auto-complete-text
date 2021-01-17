from collections import deque
import os


def process_input(dir_path, trie):
    dirs = deque([dir_path])
    while len(dirs) > 0:
        curr_dir = dirs.popleft()
        curr_files = os.listdir(curr_dir)
        for file in curr_files:
            curr_path = f"{curr_dir}/{file}"
            if os.path.isdir(curr_path):
                dirs.append(curr_path)
                print(curr_path, " Is a directory")
                continue
            process_file(curr_path, trie)


def process_file(path, trie):
    with open(path, 'r+') as f:
        lines = f.readlines()
        for line in lines:
            trie.insert(line)



def all_prefixes(string):
    start, end = 0, 0
    results = []
    while start < len(string):
        if string[end] == string[end - start]:
            results.append(string[start:end + 1])
            end += 1
            if end == len(string):
                start += 1
                end = start
        else:
            start += 1
            end = start
    return results


