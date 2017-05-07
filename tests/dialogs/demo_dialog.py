#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

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
        self.add(button)



window = pyglet.window.Window()
gui = glooey.Gui(window)
dialog = TestDialog()

@run_demos.on_space(gui) #
def test_dialog():
    dialog.open(gui)
    yield "Click on the dialog to close it."

pyglet.app.run()


