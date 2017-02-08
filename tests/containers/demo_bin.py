#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
bin = glooey.Bin()
widget = glooey.PlaceHolder(100, 100)

bin.add(widget)
root.add(bin)

@demo_helpers.interactive_tests(window, batch) 
def interactive_bin_tests():
    bin.add(widget)
    yield "Put a widget in the bin."
    bin.clear()
    yield "Clear the bin."


pyglet.app.run()


