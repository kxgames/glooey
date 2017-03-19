#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
widget = glooey.Image()
gui.add(widget)

@run_demos.on_space(gui) #
def test_image():
    widget.image = pyglet.image.load('assets/misc/star_5.png')
    yield "Show a green star."

    widget.image = pyglet.image.load('assets/misc/star_7.png')
    yield "Show a orange star."

pyglet.app.run()

