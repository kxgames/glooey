#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

widget = glooey.Placeholder()
gui.add(widget)

pyglet.app.run()

