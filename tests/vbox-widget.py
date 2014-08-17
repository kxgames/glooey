#!/usr/bin/env python

import pyglet
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
vbox = VBox(padding=5)

vbox.add(PlaceHolder(color=green, height=320))
vbox.add(PlaceHolder(color=blue), expand=True)
vbox.add(PlaceHolder(color=yellow), expand=True)
vbox.add_front(PlaceHolder(color=red), expand=True)

root.add(vbox)

pyglet.app.run()


