#!/usr/bin/env python3

import pyglet
import demo_helpers
from glooey import *
from glooey.drawing import *
from pprint import pprint

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

gui = Gui(window, batch=batch)
vbox = VBox()
gui.add(vbox)

@demo_helpers.interactive_tests(window, batch) #
def interactive_vbox_tests():

    # Test adding and removing widgets.
    for i in range(2):
        vbox.add(EventLogger(50, 50))
    yield "Make an VBox with 2 cells."

    top = EventLogger(50, 50, orange)
    vbox.add_top(top)
    yield "Add a orange widget on the top."

    bottom = EventLogger(50, 50, orange)
    vbox.add_bottom(bottom)
    yield "Add a orange widget on the bottom."

    middle = EventLogger(50, 50, orange)
    vbox.insert(middle, 2)
    yield "Insert a orange widget in the middle."

    vbox.replace(middle, EventLogger(50, 50, green))
    yield "Replace the orange widget in the middle with a green one."

    vbox.remove(top)
    yield "Remove the widget on the top."

    vbox.remove(bottom)
    yield "Remove the widget on the bottom."
    
    # Test padding.
    vbox.padding = 10
    yield "Pad the widgets by 10px."
    vbox.padding = 0

    vbox.cell_padding = 10
    yield "Only pad between the widgets."
    vbox.cell_padding = 0

    # Test alignment.
    vbox.alignment = 'center'
    yield "Center-align the whole VBox."
    vbox.alignment = 'fill'

    vbox.cell_alignment = 'center'
    yield "Center-align the widgets."
    vbox.cell_alignment = 'fill'

    # Get ready to restart the tests (and make sure clear() works).
    vbox.clear()
    yield "Clear the VBox."

pyglet.app.run()


