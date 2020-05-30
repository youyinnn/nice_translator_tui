#!/usr/bin/env python
"""
A simple example of a calculator program.
This could be used as inspiration for a REPL.
"""
from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea
from prompt_toolkit.formatted_text import FormattedText
from threading import Lock, Thread
import time

import nice_translator_tui.translate as translate
import pkg_resources

def run():
    line_cursor_pos = 0
    current_line = 0
    cursor_lock = Lock()
    during_accept = False

    # The layout.
    output_field = TextArea(
        style="class:output-field"
    )
    input_field = TextArea(
        height=1,
        prompt=" # ",
        style="class:input-field",
        multiline=False,
        wrap_lines=False,
    )

    roll = ['\\', '-', '/', '|']
    current_roll = -1
    def get_statusbar_text():
        nonlocal during_accept, current_roll
        if during_accept:
            if current_roll == 3:
                current_roll = -1
            current_roll = current_roll + 1
            return ' {} Searching...'.format(roll[current_roll])
        else:
            return ' = Nice Translator'

    def get_statusbar_class():
        nonlocal during_accept
        if during_accept:
            return "class:searching-status"
        else:
            return "class:status"

    container = HSplit(
        [
            input_field,
            Window(height=1, char="-", style="class:line"),
            output_field,
            Window(
                FormattedTextControl(get_statusbar_text),
                height=1,
                style=get_statusbar_class
            ),
        ]
    )

    def addline(old, newline):
        return old + '   {}\n'.format(newline)

    def accept(buff):
        with cursor_lock:
            nonlocal during_accept
            during_accept = True
            nonlocal line_cursor_pos
            nonlocal current_line
            line_cursor_pos = 0
            current_line = 0

            new_text = ''
            if input_field.text.strip() != '':
                try:
                    translate_result = translate.translate(input_field.text)
                    output = ''
                    for rs in translate_result:
                        output = addline(output, rs)
                    text = output
                    text_lines = text.splitlines(keepends=True)
                    for i, l in enumerate(text_lines):
                        if (l.startswith(' > ')):
                            text_lines[i] = '   ' + text_lines[i][3:]
                            break
                    text = ''.join(text_lines)
                    new_text = ' > ' + text[3:]
                except Exception as e:
                    new_text = 'Some error occured.\n{}'.format(e)

            # Add text to output buffer.
            output_field.buffer.document = Document(
                text=new_text, cursor_position=line_cursor_pos
            )
            during_accept = False

    def threading_accept(buff):
        l = [buff]
        t = Thread(target=accept, args=l)
        t.start()

    input_field.accept_handler = threading_accept

    # The key bindings.
    kb = KeyBindings()

    # show where the cursor is 
    # @kb.add("tab")
    # def _(event):
    #     event.app.layout.focus_next()

    @kb.add('escape', 'q')
    def _(event):
        " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
        event.app.exit()


    # cursor move next line
    @kb.add('escape', 'n')
    def _(event):
        with cursor_lock:
            nonlocal line_cursor_pos
            nonlocal current_line
            new_text = ''
            lines = output_field.text.splitlines(keepends=True)
            if len(lines) == 0 or current_line is len(lines) - 1:
                return
            for i, l in enumerate(lines):
                if i == current_line:
                    lines[i] = '   ' + lines[i][3:]
                    lines[i + 1] = ' > ' + lines[i + 1][3:]
                new_text = new_text + lines[i]
            line_cursor_pos = line_cursor_pos + len(lines[current_line])
            current_line = current_line + 1
            output_field.buffer.document = Document(
                text=new_text, cursor_position=line_cursor_pos
            )

    # cursor move previous line
    @kb.add('escape', 'm')
    def _(event):
        with cursor_lock:   
            nonlocal line_cursor_pos
            nonlocal current_line
            new_text = ''
            lines = output_field.text.splitlines(keepends=True)
            if current_line is 0:
                return
            for i, l in enumerate(lines):
                if i == current_line:
                    lines[i] = '   ' + lines[i][3:]
                    lines[i - 1] = ' > ' + lines[i - 1][3:]
                    break
            for l in lines:
                new_text = new_text + l
            line_cursor_pos = line_cursor_pos - len(lines[current_line - 1])
            current_line = current_line - 1
            output_field.buffer.document = Document(
                text=new_text, cursor_position=line_cursor_pos
            )

    # Style.
    style = Style(
        [
            ("output-field", ""),
            ("input-field", ""),
            ("line", "#ffffff"),
            ("status",  "bg:grey #fff"),
            ("searching-status", "bg:purple #fff")
        ]
    )

    # Run application.
    application = Application(
        layout=Layout(container),
        key_bindings=kb,
        style=style,
        full_screen=True,
        refresh_interval=0.3
    )

    application.run()

def get_config_file_path():
    print(pkg_resources.resource_filename(__name__, "config.json"))