#!/usr/bin/env python3

import pyglet
import run_demos
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
frame = golden.SmallFrame()
vbox = golden.VBox()

vbox.add(golden.Form())
# If there's text, I get a spurious cursor...
vbox.add(golden.Form('text'))
vbox.cell_alignment = 'fill horz'
frame.add(vbox)
gui.add(frame)

pyglet.app.run()


