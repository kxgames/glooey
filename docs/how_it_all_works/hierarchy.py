#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()

gui = glooey.Gui(window)
hbox = glooey.HBox(); hbox.padding = 10
left = glooey.Placeholder()
right = glooey.Placeholder()

hbox.add(left)
hbox.add(right)
gui.add(hbox)

pyglet.app.run()

