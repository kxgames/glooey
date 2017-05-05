#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

label = glooey.Label('Hello world!')
gui.add(label)

pyglet.app.run()

