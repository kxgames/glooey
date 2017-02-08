#!/usr/bin/env python3

"""An image of a green checkmark should appear in the middle of the screen.  
Scrolling should change the image to a green cross."""

import pyglet
import glooey
import demo_helpers

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.Image()
root.add(widget)

@demo_helpers.interactive_tests(window, batch) #
def test_image():
    widget.image = pyglet.image.load('green_checkmark.png')
    yield "Show a green checkmark."

    widget.image = pyglet.image.load('green_cross.png')
    yield "Show a green cross."

pyglet.app.run()

