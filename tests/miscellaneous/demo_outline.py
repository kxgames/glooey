#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
outline = glooey.Outline(color='orange')
widget = glooey.PlaceHolder(50, 50, color='green')

outline.add(widget)
root.add(outline)

@demo_helpers.interactive_tests(window, batch) #
def test_image():
    outline.bin.padding = 0
    yield "A orange outline around a green placeholder."

    outline.bin.padding = 5
    yield "Pad inside the outline."

pyglet.app.run()

