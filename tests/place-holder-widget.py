#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.PlaceHolder()
root.add(widget)

pyglet.app.run()

