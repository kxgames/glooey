#!/usr/bin/env python

"""A single place-holder should be displayed."""

import pyglet
import glooey
import test_helpers

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
bin = glooey.Bin(padding=5)
widget = glooey.PlaceHolder(100, 100)

bin.add(widget)
root.add(bin)

test_helpers.install_padding_hotkeys(window, bin)
test_helpers.install_placement_hotkeys(window, bin)

pyglet.app.run()


