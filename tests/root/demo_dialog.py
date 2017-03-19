#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
gui = glooey.Gui(window)

class TestDialog(glooey.Dialog):

    def __init__(self):
        super().__init__()
        button = glooey.Button()
        button.size_hint = 100, 100
        button.set_background(
                base_color='green',
                over_color='orange',
                down_color='purple',
        )
        button.push_handlers(on_click=lambda w: self.close())
        self._attach_child(button)



dialog = TestDialog()

@demo_helpers.interactive_tests(window, gui.batch) #
def test_dialog():
    dialog.open(gui)
    yield "Click on the dialog to close it."

pyglet.app.run()


