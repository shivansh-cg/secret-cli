from completer import CustomCompleter
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, FloatContainer, Float
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.widgets import (
    TextArea,
    Frame
)
from prompt_toolkit.layout.menus import CompletionsMenu


class cliApp:
    
    def _enter_press(self, buffer):
        self.right_buffer.text = buffer.text
        
    def __init__(self, creds) -> None:
        self.right_buffer = Buffer()
        self.completer = CustomCompleter(creds)
        self.left_window = Frame(TextArea(multiline=False, completer=self.completer, accept_handler=self._enter_press))
        self.right_window = Window(BufferControl(buffer=self.right_buffer))
        # self.body = HSplit([
        #         Window(
        #             height=1,
        #             content=FormattedTextControl("Secret-cli"),
        #             align=WindowAlign.CENTER,
        #         ),
        #         # Horizontal separator.
        #         Window(height=1, char="-", style="class:line"),
        self.body = FloatContainer(
           
                    
                    VSplit(
                    [
                        self.left_window,
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
        # ])
                                   
        
        self.app = Application(
            layout=Layout(self.body, focused_element=self.left_window),
            full_screen=True,
            # key_bindings=,
        )
        
    def run(self):
        self.app.run()
    
    def exit(self):
        self.app.exit()
        
    
    