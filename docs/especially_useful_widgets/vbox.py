#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

vbox = glooey.VBox()
vbox.add(glooey.Placeholder())
vbox.add(glooey.Placeholder())

gui.add(vbox)

pyglet.app.run()
