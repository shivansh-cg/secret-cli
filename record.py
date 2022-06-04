from copyreg import constructor
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

from prompt_toolkit.formatted_text import (
    to_formatted_text
)
from prompt_toolkit.styles import Style
from radios import MyRadio
from prompt_toolkit.layout.menus import CompletionsMenu


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
    
    def init_completer(self):
        
        meta_dict = {
            'add': "Add a new Property",
            'copy': "Copy Property",
            'edit': "Copy Property",
            'info': "Searchable Property",
            'edit info': "Searchable Property",
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
            "info": {key: None for key in self.record['info']},
            "secret": {key: None for key in self.record['secret']},
        }
        
        completor = {command: comm_completor for command in [ 'edit', 'copy']}
        completor['add'] = None
        self.comand_completer = NestedCompleter.from_nested_dict(completor, meta_dict)
    
    def command_entered(self, text):
        # self.right_buffer.text+=text.text
        self.left_window.title = text.text
        self.log_buffer.text = f'{text.text}\n{self.log_buffer.text}'
        # self.log_buffer.text += text.text
        # self.log_buffer.text +='\n'
    def layout(self):   
        self.init_completer()
        
        self.right_buffer = Buffer()
        self.log_buffer = Buffer()
        self.command_window = TextArea(
            prompt=">>> ",
            style="class:input-field",
            multiline=False,
            wrap_lines=True,
            complete_while_typing=True,
            completer=self.comand_completer,
            accept_handler=self.command_entered
        )


        # 1. First we create the layout
        #    --------------------------
        self.style = Style([
            ('input-field', '#44ff44 '),
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
                        content=CompletionsMenu(max_height=16, scroll_offset=1),
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
    
    def __init__(self, record) -> None:
        self.record = record
        self.title = "Hello Hi Question??/"
        self.layout()
        self.right_buffer.text = json.dumps(record, indent=4)
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