#!/usr/bin/env python

import pyglet
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
hbox = HBox(padding=5)

hbox.add(PlaceHolder(color=green, width=320))
hbox.add(PlaceHolder(color=blue), expand=True)
hbox.add(PlaceHolder(color=yellow), expand=True)
hbox.add_front(PlaceHolder(color=red), expand=True)

root.add(hbox)

pyglet.app.run()


