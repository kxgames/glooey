#!/usr/bin/env python

import pyglet
import test_helpers
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
hbox = HBox(padding=10)

hbox.add(PlaceHolder(320, 10, color=green), placement='fill')
hbox.add(PlaceHolder(10, 10, color=blue), expand=True)
hbox.add(PlaceHolder(10, 10, color=yellow), expand=True)
hbox.add_front(PlaceHolder(10, 10, color=red), expand=True)

root.add(hbox)

test_helpers.install_padding_hotkeys(window, hbox)
test_helpers.install_placement_hotkeys(window, hbox)

pyglet.app.run()


