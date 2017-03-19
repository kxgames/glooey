#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
outline = glooey.Outline(color='orange')
widget = glooey.PlaceHolder(50, 50, color='green')

outline.add(widget)
gui.add(outline)

@run_demos.on_space(gui) #
def test_image():
    outline.bin.padding = 0
    yield "A orange outline around a green placeholder."

    outline.bin.padding = 5
    yield "Pad inside the outline."

pyglet.app.run()

