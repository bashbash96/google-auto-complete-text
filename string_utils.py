import re


def get_text_suffixes(text):
    """
    Function to get all the suffixes substrings of a given string
    :param text: the original string
    :return: list of all suffixes
    """
    words = text.split(' ')
    suffixes = []
    for i in range(len(words)):
        if words[i] in words[0:i]:
            continue
        sentence = ' '.join(words[i:])
        suffixes.append(sentence)

    return suffixes


def lev_distance(text1, text2):
    """
    return the minimum distance between two strings using Levenshtein Algorithm
    the distance is the number of operations (insertion, deletion, substitution) we
    need to do to the first string in order to get the second one.
    :param text1: first string
    :param text2: second string
    :return: minimum distance
    """

    n, m = len(text1), len(text2)
    # distances = [[j for j in range(m + 1)] for _ in range(n + 1)]
    #
    # for row in range(1, n + 1):
    #     for col in range(1, m + 1):
    #         # if they are equal take the previous distance.
    #         if text1[row - 1] == text2[col - 1]:
    #             distances[row][col] = distances[row - 1][col - 1]
    #         else:
    #             # if they are not equal the distance is 1 + the minimum between:
    #             # 1- insert new letter (row - 1, col)
    #             # 2- delete letter (row, col - 1)
    #             # substitute the letter with the other (row - 1, col - 1)
    #             distances[row][col] = min(distances[row - 1][col - 1],
    #                                       min(distances[row][col - 1], distances[row - 1][col])) + 1
    #
    # return distances[n][m]

    # optimized space to O(m)
    prev_distances = [i for i in range(m + 1)]
    curr_distances = []
    for row in range(1, n + 1):
        curr_distances = [row]
        for col in range(1, m + 1):
            # if they are equal take the previous distance.
            if text1[row - 1] == text2[col - 1]:
                curr_distances.append(prev_distances[col - 1])
            else:
                # if they are not equal the distance is 1 + the minimum between:
                # 1- insert new letter (row - 1, col)
                # 2- delete letter (row, col - 1)
                # 3- substitute the letter with the other (row - 1, col - 1)
                min_distance = min(prev_distances[col - 1], min(curr_distances[col - 1], prev_distances[col]))
                curr_distances.append(min_distance + 1)
        prev_distances = curr_distances

    return curr_distances[m]

    # Time O(n * m)
    # Space O(m)


def clean_text(text):
    """
    clean all non-needed characters
    :param text: original text
    :return: filtered text
    """

    # Take the text as lower
    text = text.lower()

    # Remove white spaces
    text = text.encode('ascii', 'ignore').decode('ascii')
    white_spaces = re.compile("\s+")
    text = white_spaces.sub(' ', text)

    # remove \n
    text = text.replace('\n', '')

    # Remove leading and trailing spaces and last enter
    return text.strip()


def get_text_from_path(path, idx):
    """
    get a specific line from a specific file by its path and its index
    :param path: file path
    :param idx: line index
    :return: result line
    """

    with open(path, 'r+', encoding="utf8") as fid:
        lines = fid.readlines()
        if idx >= 0 and idx < len(lines):
            return lines[idx]
    return ''
