#!/usr/bin/env python

"""A green box with a cross should take up most of the screen."""

import pyglet
import glooey

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
root.padding = 50
widget = glooey.PlaceHolder()
root.add(widget)

pyglet.app.run()

