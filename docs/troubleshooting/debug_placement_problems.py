#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)
gui.padding = 50

widget = glooey.Placeholder(200, 100)
widget.alignment = 'top left'

gui.add(widget)
widget.debug_placement_problems()

pyglet.app.run()
