#!/usr/bin/env python3

"""\
A single place-holder should take up the full window.  Pressing space should 
toggle whether or not that place-holder is attached to the GUI."""

import pyglet
import glooey
import demo_helpers

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
bin = glooey.Bin()
widget = glooey.PlaceHolder(100, 100)

bin.add(widget)
root.add(bin)

i = 0
@window.event
def on_key_press(symbol, modifiers): #
    if symbol == pyglet.window.key.SPACE:
        global i

        if i == 0:
            bin.clear()
        if i == 1:
            bin.add(widget)

        i = (i + 1) % 2

pyglet.app.run()


