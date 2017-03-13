#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
radio = golden.RadioButton()
gui.add(radio)

pyglet.app.run()


