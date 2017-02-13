#!/usr/bin/env python3

import pyglet
import demo_helpers
import glooey.themes.golden as golden

window = pyglet.window.Window()
root = golden.Gui(window)
button = golden.BasicButton('Lorem Ipsum')
root.add(button)

pyglet.app.run()


