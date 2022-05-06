import base64
import json
import os
import threading
from base64 import b64encode,b64decode

from prompt_toolkit import prompt
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.validation import Validator
from prompt_toolkit.completion import PathCompleter
 
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken

def toggle_input(prompt_text=">", initially_hidden=True):
    """Input Prompt which has a toggle to show input characters or not

    Args:
        prompt_text (str, optional): Text to be shown for the prompt. Defaults to ">".
        initially_hidden (bool, optional): Initial state of visibility for the input. Defaults to True.

    Returns:
        str: Input text from the prompt
    """

    hidden = [initially_hidden]  
    bindings = KeyBindings()

    @bindings.add("c-t")
    def _(event):
        "When Ctrl-T has been pressed, toggle visibility."
        hidden[0] = not hidden[0]

    input_text = prompt(
        prompt_text, rprompt="Ctrl-T to toggle visibility", is_password=Condition(lambda: hidden[0]), key_bindings=bindings
    )
    return input_text


def get_path_prompt(prompt_text, **kwargs):
    """Prompt for taking OS Path as input

    Args:
        prompt_text (str): Display text when taking input
        **kwargs : extra arguments to be sent to `prompt` function

    Returns:
        str: input path from the prompt
    """
    validator = Validator.from_callable(
        os.path.isdir,
        error_message="Not a valid path to a directory",
        move_cursor_to_end=True,
    )

    return prompt(
                prompt_text,
                completer=PathCompleter(only_directories=True), 
                rprompt="Press Tab to get suggestions",
                validator=validator,
                validate_while_typing=True, **kwargs)

