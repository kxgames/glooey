#!/usr/bin/env python3

import glooey
import pyglet

class MyPlaceholder(glooey.Placeholder):
    custom_size_hint = 300, 200  # width, height
    custom_alignment = 'center'

window = pyglet.window.Window()
gui = glooey.Gui(window)

widget = MyPlaceholder()
gui.add(widget)

pyglet.app.run()

