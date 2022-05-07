from prompt_toolkit.completion import Completer
from prompt_toolkit.document import Document
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit import prompt
import json

import re


class CustomCompleter(Completer):
    """
        Custom completer for filling the completion

    """

    def __init__(
        self, cred_list, ignore_case = True, last_input = ''
    ) -> None:

        self.ignore_case = ignore_case
        self.cred_list = cred_list
        self.last_input = last_input
        self.narrow_options()

    def narrow_options(self):
        self.my_word_dict = {}
        for c in self.cred_list:
            for k in c['info']:
                the_key = k+":"+c['info'][k]
                # if the_key == self.last_input:
                #     continue
                if the_key in self.my_word_dict:
                    self.my_word_dict[the_key].append(c)
                else:
                    self.my_word_dict[the_key] = [c]
                
    def get_completions(
        self, document, complete_event
    ):
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # If there is a space, check for the first term, and use a
        # subcompleter.
        if " " in text:
            first_term = text.split()[0]
            completer = CustomCompleter(cred_list=self.my_word_dict[first_term], last_input=first_term)

            # If we have a sub completer, use this for the completions.
            if completer is not None:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                yield from completer.get_completions(new_document, complete_event)

        # No space in the input: behave exactly like `WordCompleter`.
        else:
            completer = FuzzyCompleter(completer=WordCompleter(self.my_word_dict.keys()),enable_fuzzy=True, pattern=r"^([a-zA-Z0-9_:]+|[^a-zA-Z0-9_\s]+)")
            
            yield from completer.get_completions(document, complete_event)


if __name__ == "__main__":
    creds = []

    with open("user_cred.json", "r") as file:
        creds = json.loads(file.read())
        
    text = prompt('Enter : ', completer=CustomCompleter(creds))
    print( (text).split(' '))