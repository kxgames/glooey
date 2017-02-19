#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
root.padding = 50
widget = glooey.PlaceHolder()
root.add(widget)

pyglet.app.run()

