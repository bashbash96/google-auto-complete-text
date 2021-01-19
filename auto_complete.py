from dataclasses import dataclass


@dataclass
class AutoCompleteData:
    """
    completed_sentence: the full sentence
    source_text: the path of the source file of the sentence
    offset: the offset of the user input from the full sentence
    score: the final score of the sentence
    """
    completed_sentence: str
    source_text: str
    offset: int
    score: int
