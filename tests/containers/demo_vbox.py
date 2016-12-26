#!/usr/bin/env python

import pyglet
import demo_helpers
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
vbox = VBox(padding=10)

vbox.add(PlaceHolder(10, 320, color=green), placement='fill')
vbox.add(PlaceHolder(10, 10, color=blue), expand=True)
vbox.add(PlaceHolder(10, 10, color=yellow), expand=True)
vbox.add_front(PlaceHolder(10, 10, color=red), expand=True)

root.add(vbox)

demo_helpers.install_padding_hotkeys(window, vbox)
demo_helpers.install_placement_hotkeys(window, vbox)

pyglet.app.run()


