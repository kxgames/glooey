#!/usr/bin/env python3

import pyglet
import test_helpers
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
stack = Stack()
stack.placement = 'center'

stack.add(PlaceHolder(400, 400, color=blue))
stack.add(PlaceHolder(350, 350, color=green))
stack.add(PlaceHolder(300, 300, color=yellow))
stack.add(PlaceHolder(250, 250, color=orange))
stack.add(PlaceHolder(200, 200, color=red))

root.add(stack)

test_helpers.install_padding_hotkeys(window, stack)
test_helpers.install_placement_hotkeys(window, stack)

pyglet.app.run()

