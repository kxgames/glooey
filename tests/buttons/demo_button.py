#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestButton(glooey.Button): #

    class Label(glooey.Label): #
        custom_color = '#deeed6'
        custom_font_size = 14
        custom_bold = True
        custom_padding = 20

    class Base(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/green.png')

    class Over(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/orange.png')

    class Down(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/purple.png')

    class Off(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/grey.png')


window = pyglet.window.Window()
gui = glooey.Gui(window)
button = TestButton('Hello world!')
gui.add(button)

@button.event #
def on_click(widget):
    print("{} clicked!".format(widget))

@button.event #
def on_double_click(widget):
    print("{} double clicked!".format(widget))

@run_demos.on_space(gui) #
def test_button():
    yield "Green button with orange over and purple down states."
    button.deactivate()
    yield "Grey inactive button (no rollover)."
    button.reactivate()

pyglet.app.run()

