#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
root = golden.Gui(window)
radio = golden.RadioButton()
root.add(radio)

pyglet.app.run()


