#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
label = golden.Label("Hello world!")
label.alignment = 'center'
gui.add(label)

pyglet.app.run()


