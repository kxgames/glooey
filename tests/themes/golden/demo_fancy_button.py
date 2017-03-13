#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
button = golden.FancyButton('lorem ipsum')
gui.add(button)

pyglet.app.run()


