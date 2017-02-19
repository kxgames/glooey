#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.Image()
root.add(widget)

@demo_helpers.interactive_tests(window, batch) #
def test_image():
    widget.image = pyglet.image.load('assets/misc/star_5.png')
    yield "Show a green star."

    widget.image = pyglet.image.load('assets/misc/star_7.png')
    yield "Show a orange star."

pyglet.app.run()

