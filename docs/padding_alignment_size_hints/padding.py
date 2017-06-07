#!/usr/bin/env python3

import glooey
import pyglet

class MyPlaceholder(glooey.Placeholder):
    custom_padding = 10

window = pyglet.window.Window()
gui = glooey.Gui(window)

widget = MyPlaceholder()
gui.add(widget)

pyglet.app.run()

