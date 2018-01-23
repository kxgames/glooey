#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

widget = glooey.Placeholder()
widget.alignment = 'top left'

gui.add(widget)
widget.debug_drawing_problems()

pyglet.app.run()
