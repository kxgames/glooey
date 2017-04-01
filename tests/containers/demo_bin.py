#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
bin = glooey.Bin()
widget = glooey.Placeholder(100, 100)

bin.add(widget)
gui.add(bin)

@run_demos.on_space(gui) 
def test_bin():
    bin.add(widget)
    yield "Put a widget in the bin."
    bin.clear()
    yield "Clear the bin."


pyglet.app.run()


