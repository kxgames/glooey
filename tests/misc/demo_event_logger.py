#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
gui = glooey.Gui(window)
gui.padding = 50
widget = glooey.EventLogger()
gui.add(widget)

pyglet.app.run()

