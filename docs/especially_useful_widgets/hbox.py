#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

hbox = glooey.HBox()
hbox.add(glooey.Placeholder())
hbox.add(glooey.Placeholder())

gui.add(hbox)

pyglet.app.run()
