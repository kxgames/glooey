#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

gui = glooey.Gui(window, batch=batch)
widget = glooey.PlaceHolder()
gui.add(widget)

@demo_helpers.interactive_tests(window, batch) #
def interactive_padding_tests():
    # Test setting and change the size hints.
    w = glooey.PlaceHolder(50, 50)
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

    class Widget200x0(glooey.PlaceHolder): #
        custom_alignment = 'center'
        custom_width_hint = 200

    gui.clear(); gui.add(Widget200x0(50, 50))
    yield "A custom 200x50 placeholder."

    class Widget0x100(glooey.PlaceHolder): #
        custom_alignment = 'center'
        custom_height_hint = 100

    gui.clear(); gui.add(Widget0x100(50, 50))
    yield "A custom 50x100 placeholder."

    class Widget200x100(glooey.PlaceHolder): #
        custom_alignment = 'center'
        custom_size_hint = 200, 100

    gui.clear(); gui.add(Widget200x100(50, 50))
    yield "A custom 200x100 placeholder."

pyglet.app.run()


