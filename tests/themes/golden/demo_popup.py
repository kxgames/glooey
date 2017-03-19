#!/usr/bin/env python3

import pyglet
import run_demos
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
popup = golden.PopUp('Lorem ipsum\ndolor sit amet.')

@run_demos.on_space(gui) #
def test_popup():
    popup.open(gui)
    yield "Open the popup.  Click the 'X' to close it."

pyglet.app.run()


