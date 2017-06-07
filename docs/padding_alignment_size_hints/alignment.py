#!/usr/bin/env python3

import glooey
import pyglet

class MyPlaceholder(glooey.Placeholder):
    custom_alignment = 'center'

window = pyglet.window.Window()
gui = glooey.Gui(window)

widget = MyPlaceholder(300, 200)
gui.add(widget)

pyglet.app.run()

