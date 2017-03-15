#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
box = golden.ScrollBox()
label = golden.Label(golden.drawing.lorem_ipsum(), 400)

box.alignment = 'center'
box.height_hint = gui.territory.height - 100

box.add(label)
gui.add(box)

pyglet.app.run()



