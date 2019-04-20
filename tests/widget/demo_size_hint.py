#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
widget = glooey.Placeholder()
gui.add(widget)

@run_demos.on_space(gui)
def test_size_hint():
    # Test setting and change the size hints.
    w = glooey.Placeholder(50, 50)
    w.alignment = 'center'
    gui.clear(); gui.add(w)
    yield "A 50x50 placeholder."

    w.width_hint = 200
    yield "A 200x50 placeholder."
    w.width_hint = 0

    w.height_hint = 100
    yield "A 50x100 placeholder."
    w.height_hint = 0

    w.size_hint = 200, 100
    yield "A 200x100 placeholder."
    w.size_hint = 0, 0

    # Test setting class-wide custom size hints.

    class Widget200x0(glooey.Placeholder): #
        custom_alignment = 'center'
        custom_width_hint = 200

    gui.clear(); gui.add(Widget200x0(50, 50))
    yield "A custom 200x50 placeholder."

    class Widget0x100(glooey.Placeholder): #
        custom_alignment = 'center'
        custom_height_hint = 100

    gui.clear(); gui.add(Widget0x100(50, 50))
    yield "A custom 50x100 placeholder."

    class Widget200x100(glooey.Placeholder): #
        custom_alignment = 'center'
        custom_size_hint = 200, 100

    gui.clear(); gui.add(Widget200x100(50, 50))
    yield "A custom 200x100 placeholder."

pyglet.app.run()


