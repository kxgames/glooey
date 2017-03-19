#!/usr/bin/env python3

import pyglet
import demo_helpers
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
popup = golden.PopUp('Lorem ipsum\ndolor sit amet.')

@demo_helpers.interactive_tests(window, gui.batch) #
def test_popup():
    popup.open(gui)
    yield "Open the popup.  Click the 'X' to close it."

pyglet.app.run()


