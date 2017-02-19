#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestButton(glooey.Button): #
    default_alignment = 'center'

    class Label(glooey.Label):
        default_color = '#deeed6'
        default_font_size = 14
        default_bold = True
        default_padding = 20

    class Base(glooey.Background):
        default_center = pyglet.image.load('assets/64x64/green.png')

    class Over(glooey.Background):
        default_center = pyglet.image.load('assets/64x64/orange.png')

    class Down(glooey.Background):
        default_center = pyglet.image.load('assets/64x64/purple.png')

    class Off(glooey.Background):
        default_center = pyglet.image.load('assets/64x64/grey.png')

root = glooey.Gui(window, batch=batch)
button = TestButton('Hello world!')
root.add(button)

@button.event #
def on_click(widget):
    print("{} clicked!".format(widget))

@button.event #
def on_double_click(widget):
    print("{} double clicked!".format(widget))

@demo_helpers.interactive_tests(window, batch) #
def test_checkbox():
    yield "Green button with orange over and purple down states."
    button.deactivate()
    yield "Grey inactive button (no rollover)."
    button.reactivate()

pyglet.app.run()

