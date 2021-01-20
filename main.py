from index_writer import write_index
from index_reader import read_index
from string_utils import clean_text


def is_valid(user_input):
    """
    check if the user input is valid
    :param user_input: string
    :return: True/False
    """
    return len(user_input) > 0


def get_valid_input():
    """
    return valid user input
    :return: user input
    """

    while True:
        user_input = input()
        if is_valid(user_input):
            return user_input

def print_suggestions(res):
    """
    function to print suggestion for the user
    :param res: list of results
    :return: None
    """
    if len(res) == 0:
        print("There is no suggestions")
        return
    if len(res) == 1:
        print(f"Here is one suggestions:")
    else:
        print(f"Here are {len(res)} suggestions:")
    for idx, val in enumerate(res):
        print(f"{idx + 1}. {val.completed_sentence}")


def main():
    """
    the main function
    :return: None
    """

    trie = write_index("Input/")
    user_input = ''
    # trie = read_index(path)
    print("The System is ready. Enter your text:")
    while True:
        user_input += clean_text(get_valid_input())
        if user_input[-1] == '#':
            user_input = ''
            continue
        if user_input[-2:] == '#q':
            break
        print_suggestions(trie.get_best_k_completions(user_input))
        print(user_input, end='')


main()
