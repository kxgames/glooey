#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
widget = glooey.Placeholder()
gui.add(widget)

@run_demos.on_space(gui) #
def test_padding():
    widget.padding = 100
    yield "padding = 100 px"
    widget.set_padding(left=100)
    yield "left padding = 100 px"
    widget.set_padding(right=100)
    yield "right padding = 100 px"
    widget.set_padding(top=100)
    yield "top padding = 100 px"
    widget.set_padding(bottom=100)
    yield "bottom padding = 100 px"
    widget.set_padding(horz=100)
    yield "horizontal padding = 100 px"
    widget.set_padding(vert=100)
    yield "vertical padding = 100 px"

pyglet.app.run()


