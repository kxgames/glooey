#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

gui = glooey.Gui(window, batch=batch)
gui.padding = 50
widget = glooey.PlaceHolder()
gui.add(widget)

pyglet.app.run()

