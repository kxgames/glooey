#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
widget = glooey.Placeholder()
gui.add(widget)

@run_demos.on_space(gui)
def test_place_holder():
    widget.color = 'green'
    yield 'green placeholder.'

    widget.color = 'orange'
    yield 'orange placeholder.'



pyglet.app.run()

