#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
root = glooey.Gui(window)
widget = glooey.EventLogger(100, 100, align='center')
root.add(widget)

pyglet.app.run()


