import utils
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout

from prompt_toolkit.layout.margins import (
    ConditionalMargin,
    NumberedMargin,
    ScrollbarMargin,
)
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
password = utils.toggle_input("Master Password")
print(password)

aal = 1
class MyRadio(RadioList):
    open_character = ""
    close_character = ""
    
    def __init__(self, values, default = None) -> None:
        super().__init__(values, default)
        
        # Key bindings.
        kb = KeyBindings()

        @kb.add("up")
        def _up(event) -> None:
            self._selected_index = max(0, self._selected_index - 1)
            right_buffer.text = self.values[self._selected_index][0]

        @kb.add("down")
        def _down(event) -> None:
            self._selected_index = min(len(self.values) - 1, self._selected_index + 1)
            right_buffer.text = self.values[self._selected_index][0]


        @kb.add("enter")
        @kb.add(" ")
        def _click(event) -> None:
            event.app.exit(self.values[self._selected_index][0])
            # self._handle_enter()
            
        self.control = FormattedTextControl(
            self._get_text_fragments, key_bindings=kb, focusable=True
        )
        self.window = Window(
            content=self.control,
            style=self.container_style,
            right_margins=[
                ConditionalMargin(
                    margin=ScrollbarMargin(display_arrows=True),
                    filter=Condition(lambda: self.show_scrollbar),
                ),
            ],
            dont_extend_height=True,
        )

    def _get_text_fragments(self) :
        result = []
        for i, value in enumerate(self.values):
            if self.multiple_selection:
                checked = value[0] in self.current_values
            else:
                checked = value[0] == self.current_value
            selected = i == self._selected_index


            style = ""
            if selected:
                style += self.selected_style
                
            if selected:
                result.append(("[SetCursorPosition]", ">"))
            else:
                result.append(("", " "))

            result.append((self.default_style, " "))
            result.extend(to_formatted_text(value[1], style=style))
            result.append(("", "\n"))

        result.pop()  # Remove last newline.
        return result
    def _handle_enter(self) -> None:
        global aal
        
        right_buffer.text = f"{aal}"
        aal += 1
        global application
        application.exit()
        return super()._handle_enter()
    
   
radios = MyRadio(
    values=[
        ("Red", "red"),
        ("Green", "green"),
        ("Blue", "blue"),
        ("Orange", "orange"),
        ("Yellow", "yellow"),
        ("Purple", "Purple"),
        ("Brown", "Brown"),
    ]
)


right_buffer = Buffer()

# 1. First we create the layout
#    --------------------------
style = Style([
     ('radio-selected', '#4444ff underline bold '),
 ])

left_window = Frame(title="Radio list", body=radios, width=40)
right_window = Window(BufferControl(buffer=right_buffer))


body = VSplit(
    [
        left_window,
        # A vertical line in the middle. We explicitly specify the width, to make
        # sure that the layout engine will not try to divide the whole width by
        # three for all these windows.
        Window(width=1, char="|", style="class:line"),
        # Display the Result buffer on the right.
        right_window,
    ]
)


def get_titlebar_text():
    return [
        ("class:title", " Hello world "),
        ("class:title", " (Press [Ctrl-Q] to quit.)"),
    ]


root_container = HSplit(
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
        body,
    ]
)


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

application = Application(
    layout=Layout(root_container, focused_element=left_window),
    key_bindings=kb,
    # Let's add mouse support!
    mouse_support=True,
    # Using an alternate screen buffer means as much as: "run full screen".
    # It switches the terminal to an alternate screen.
    full_screen=True,
    style=style
)

res = application.run()

print(res)