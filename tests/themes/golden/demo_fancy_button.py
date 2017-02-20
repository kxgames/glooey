#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
root = golden.Gui(window)
button = golden.FancyButton('lorem ipsum')
root.add(button)

pyglet.app.run()


