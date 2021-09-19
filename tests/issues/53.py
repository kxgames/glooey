#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

print("Fill should be superimposed on base, not separated.")

window = pyglet.window.Window()
gui = golden.Gui(window)
bar = golden.FancyFillBar()
gui.add(bar)

bar.fraction_filled = .5

pyglet.app.run()
