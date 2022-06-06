from datetime import datetime
from posixpath import split
from wsgiref.validate import validator 
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, FloatContainer, Float
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
# from prompt_toolkit.completion import NestedCompleter
from nested_completer import NestedCompleter
from prompt_toolkit.filters import (
    Condition,
)
import json
from prompt_toolkit.widgets import (
    Box,
    Button,
    Checkbox,
    Dialog,
    Frame,
    Label,
    MenuContainer,
    MenuItem,
    ProgressBar,
    RadioList,
    TextArea,
)
from prompt_toolkit.validation import Validator, ValidationError

from prompt_toolkit.formatted_text import (
    to_formatted_text
)
from prompt_toolkit.styles import Style
from radios import MyRadio
from prompt_toolkit.layout.menus import CompletionsMenu

from utils import cred_string,  command_format_toolbar
class RecordActionValidator:
    
    def validate(document):
        len_meta = {
            "edit": 4,
            "add": 4,
            "copy": 3,
            "delete": 3,
        }
        text = document.text
        text_split = text.split()
        if len(text_split)>0 and text_split[0] in len_meta :
            if len(text_split) != len_meta[text_split[0]]:
                raise ValidationError(len(text), "Incorrect Input: {command} {type} {name} {value}")
            return
        raise ValidationError(len(text), "Incorrect Input: {command} {type} {name} {value}")
        
class RecordHandler:
    log_meta = {
        "edit": {
            "secret": "Edited Secret {}",
            "info": "Edited Info {}"
        },
        "add": {
            "secret": "Added a new Secret {}",
            "info": "Added Info {}"
        },
        "copy": {
            "secret": "Copied Secret {}",
            "info": "Copied Info {}"
        },
        "delete": {
            "secret": "Deleted Secret {}",
            "info": "Deleted Info {}"
        }
    }
    def __init__(self, record) -> None:
        self.record:dict = record
        self.last_action = []
        if 'last_updated' not in self.record:
            self.record['last_updated'] =  int(datetime.now().timestamp())
        
        if 'versioning' not in self.record:
            self.record['versioning'] = []
            
            
    def edit(self,type:str, key:str, new_val:str):
        if type == "info":
            # Info keys are swapped
            self.record[type][new_val] = key
        else:    
            self.record[type][key] = new_val
        
    def copy(self, type:str, key:str):
        # Copy the val into clipboard
        val = self.record[type][key]
        # Copy this

    def delete_prop(self, type:str, key:str):
        if type == "secret":
            self.record[type].pop(key)
        else:
            the_key = None
            for k in self.record[type]:
                if self.record[type][k] == key:
                    the_key = k
                    break
            self.record[type].pop(the_key, None)
            
    def process_input(self, input_text:str):
        split_text = input_text.split()
        self.last_action = self.log_meta[split_text[0]][split_text[1]].format(split_text[2])
        if split_text[0] == "copy":
            self.copy(split_text[1], split_text[2])
        elif split_text[0] == "delete":
            self.delete_prop(split_text[1], split_text[2])
                
        elif split_text[0] == "add" or split_text[0] == "edit":
            # Update the version history as well
            # self.record
            self.record['versioning'].append(str(hash(json.dumps(self.record))))
            self.record['last_updated'] = int(datetime.now().timestamp())
            
            # Because we have swapped the key values for info

            self.edit(split_text[1], split_text[2], split_text[3])
    
    def print(self):
        print(cred_string(self.record))

class RecordApp:
    kb = KeyBindings()


    @kb.add("c-c", eager=True)
    @kb.add("c-q", eager=True)
    def _(event):
        """
        Pressing Ctrl-Q or Ctrl-C will exit the user interface.

        Setting a return value means: quit the event loop that drives the user
        interface and return this value from the `Application.run()` call.

        Note that Ctrl-Q does not work on all terminals. Sometimes it requires
        executing `stty -ixon`.
        """
        event.app.exit()
    
    def callback(self, data):
        self.right_buffer.text = data 
    
    def input_validator(text:str):
        text_split = text.split()
        if text_split[0] == "edit" or text_split[0] == "add":
            if len(text_split)!=4:
                return False
        if text_split[0] == "delete" or text_split[0] == "copy":
            if len(text_split)!=3:
                return False

        
    def init_completer(self):
        
        meta_dict = {
            'add': "Example: add info username abcd",
            'edit': "Example: edit secret password secret_pass321",
            'copy': "Example: copy secret password",
            'delete': "Example: delete info email",
            'info': "Searchable Property",
            'secret': "Secure Property",
        }
        # completor = {
        #     "add": {
        #         "info": dict(self.record['info'].keys()),
        #         "secret": dict(self.record['secret'].keys()),
        #     },
        # }
        # completor = { {command: {"info": dict(self.record['info'].keys()), "secret": dict(self.record['secret'].keys())}} for command in ['add', 'edit', 'secret']}
        comm_completor = {
            "info": {key: None for key in self.record_handler.record['info']},
            "secret": {key: None for key in self.record_handler.record['secret']},
        }
        
        completor = {command: comm_completor for command in [ 'edit', 'copy', 'add', 'delete']}
        self.command_completer = NestedCompleter.from_nested_dict(completor, meta_dict)
    
    def command_entered(self, text: Buffer):
        
        # self.right_buffer.text+=text.text
        # self.left_window.title = text.text
        try:
            RecordActionValidator.validate(text)
            self.record_handler.process_input(text.text)
            self.invalid_input = False
        except ValidationError as ve:
            self.invalid_input = True
            self.record_handler.last_action = ve.message
            
        self.update_ui()
            
        # self.log_buffer.text += text.text
        # self.log_buffer.text +='\n'
        
    def layout(self):   
        self.init_completer()
        from prompt_toolkit.layout.processors import BeforeInput
        self.right_buffer = Buffer()
        self.log_buffer = Buffer()
        
        def vv(x):
            self.invalid_input = False
            return True
        validator = Validator.from_callable(
            vv,
            error_message=" ",
            move_cursor_to_end=True,
        )


        self.command_window = TextArea(
            
            prompt=">>> ",
            style="class:input-field",
            multiline=False,
            # wrap_lines=True,
            complete_while_typing=True,
            completer=self.command_completer,
            accept_handler=self.command_entered,
            validator=validator,
            # input_processors= 
            height=4
        )


        # 1. First we create the layout
        #    --------------------------
        self.style = Style([
            ('input-field', '#44ff44 '),
            
            ("signature-toolbar", "bg:#44bbbb #000000"),
        ])

        self.left_window = Frame(title="Your Input", body=self.command_window, width=60)
        self.right_window = Window(BufferControl(buffer=self.right_buffer))
        self.log_window = Frame(title="Logs Window", body=Window(BufferControl(buffer=self.log_buffer)))
        self.left = HSplit([
            self.left_window,
            self.log_window
            
        ])

        self.body = FloatContainer(
           
                VSplit(
                    [
                        
                        self.left,
                        Window(width=1, char="|", style="class:line"),
                        self.right_window,
                    ]
                ),
                floats=[
                    Float(
                        xcursor=True,
                        ycursor=True,
                        content = HSplit([
                           # Add this Later MAybe
                            # command_format_toolbar(self, "{command} {type} {name} {value}"),
                            CompletionsMenu(max_height=16, scroll_offset=1),
                        ])
                    )
                ],
            )
        
  


        def get_titlebar_text():
            return [
                ("class:title", " Search Results "),
                ("class:title", " (Press [Ctrl-Q] to quit.)"),
            ]

        
        self.root_container = HSplit(
            [
                # The titlebar.
                Window(
                    height=1,
                    content=FormattedTextControl(get_titlebar_text),
                    align=WindowAlign.CENTER,
                ),
                # Horizontal separator.
                Window(height=1, char="-", style="class:line"),
                # The 'body', like defined above.
                self.body,
            ]
        )
    
    def update_ui(self) -> None:
        self.right_buffer.text = cred_string(self.record_handler.record)
        self.log_buffer.text = f'{self.record_handler.last_action}\n{self.log_buffer.text}'
        
    
    def __init__(self, record) -> None:
        # self.record = record
        self.invalid_input = False
        self.record_handler = RecordHandler(record)
        self.title = "Hello Hi Question??/"
        self.layout()
        self.right_buffer.text = cred_string(self.record_handler.record)
        self.app = Application(
            layout=Layout(self.root_container, focused_element=self.left_window),
            key_bindings=self.kb,
            # Let's add mouse support!
            mouse_support=True,
            # Using an alternate screen buffer means as much as: "run full screen".
            # It switches the terminal to an alternate screen.
            full_screen=True,
            style=self.style
        )
        pass
    
    def run(self):
        """returns the result of the search

        """
        return self.app.run()
    
    def input_title(self, text):
        text = text.split()
        meta_dict = {
            "copy": "Copied"
        }
    
    def process_input(self, text):
        
        pass
    

if __name__ =="__main__":
    import json
    
    my_val = {
        "info": {
            "howard.com": "company",
            "kreeves@howard.com": "email",
            "karenchavez": "username"
        },
        "secret": { 
            "password": "I^1ZGPg7nx", 
            "token": "abcdjfcbkwe", 
            "access_id": "efasdfasf", 
            "PAT": "aswresedf" 
        }
    }
    app = RecordApp(my_val)
    print(app.run())