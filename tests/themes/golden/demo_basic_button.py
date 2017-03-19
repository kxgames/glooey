#!/usr/bin/env python3

import pyglet
import run_demos
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
button = golden.BasicButton('Lorem Ipsum')
gui.add(button)

pyglet.app.run()


