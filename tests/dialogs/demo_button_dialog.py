#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestButton(glooey.Button):
    custom_size_hint = 100, 20

    class Foreground(glooey.Label): #
        custom_color = 'white'
        custom_alignment = 'center'

    class Base(glooey.Background): #
        custom_color = 'green'

    class Over(glooey.Background): #
        custom_color = 'orange'

    class Down(glooey.Background): #
        custom_color = 'purple'

class TestOkDialog(glooey.OkDialog):
    Content = glooey.Placeholder
    custom_size_hint = 300, 200

    class Bin(glooey.Grid): #
        custom_padding = 5

    class Decoration(glooey.Background): #
        custom_outline = 'green'

    class OkButton(TestButton): #
        custom_text = 'Ok'

class TestYesNoDialog(glooey.YesNoDialog):
    Content = glooey.Placeholder
    custom_size_hint = 300, 200

    class Bin(glooey.Grid): #
        custom_padding = 5

    class Decoration(glooey.Background): #
        custom_outline = 'green'

    class Buttons(glooey.YesNoDialog.Buttons): #
        custom_cell_padding = 5

    class YesButton(TestButton): #
        custom_text = 'Yes'

    class NoButton(TestButton): #
        custom_text = 'No'


window = pyglet.window.Window()
gui = glooey.Gui(window)

@run_demos.on_space(gui) #
def test_dialog():
    ok_dialog = TestOkDialog()
    ok_dialog.open(gui)
    ok_dialog.push_handlers(on_close=lambda w: print(f"{w} closed"))
    yield 'Dialog with an "Ok" button.'
    ok_dialog.close()

    ok_dialog = TestOkDialog()
    ok_dialog.open(gui)
    ok_dialog.ok_button = TestButton(text='Custom')
    ok_dialog.push_handlers(on_close=lambda w: print(f"{w} closed"))
    yield 'Dialog with a custom "Ok" button.'
    ok_dialog.close()

    yes_no_dialog = TestYesNoDialog()
    yes_no_dialog.open(gui)
    yes_no_dialog.push_handlers(on_close=lambda w: print(f"{w} closed.  You clicked '{'yes' if w.response else 'no'}'."))
    yield 'Dialog with "Yes" and "No" buttons.'
    yes_no_dialog.close()

pyglet.app.run()
