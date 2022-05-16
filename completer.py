
from prompt_toolkit.completion import Completer
from prompt_toolkit.document import Document
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter, NestedCompleter
from prompt_toolkit import prompt
import json

import re

global_end = None
class CustomCompleter(Completer):
    """
        Custom completer for filling the completion

    """
    
    completion_callback = None

    def __init__(
        self, cred_list, commands = {}, ignore_case = True, last_inputs = set()
    ) -> None:

        self.ignore_case = ignore_case
        self.cred_list = cred_list
        self.last_inputs:set = last_inputs
        self.single_option = None
        self.narrow_options()

    def narrow_options(self):
        global global_end
        self.my_word_dict = {}
        
        if len(self.cred_list) == 1:
            self.single_option = self.cred_list[0]
            for k in c['secret']:
                self.my_word_dict[k] = []
        
        for c in self.cred_list:
            for k in c['info']:
                the_key = k+":"+c['info'][k]
                if the_key in self.last_inputs:
                    continue
                if the_key in self.my_word_dict:
                    self.my_word_dict[the_key].append(c)
                else:
                    self.my_word_dict[the_key] = [c]
        global_end = self.my_word_dict

                
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
            next_word_dict = self.my_word_dict[first_term]
            if len(next_word_dict) == 1:
                nextSecrets = next_word_dict[0]['secrets'].keys()
                commands = {
                    "copy": None,
                    "edit": None,
                    "view": None
                }
                nestedDict = dict(zip(nextSecrets, [commands for i in range(len(nextSecrets))]))
                
                completer = NestedCompleter.from_nested_dict(nestedDict)
                # yield from completer.get_completions(document, complete_event)
            else:
                self.last_inputs.add(first_term)
                completer = CustomCompleter(cred_list=self.my_word_dict[first_term], last_inputs=self.last_inputs)

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
    print(global_end)
    print( (text).split(' '))