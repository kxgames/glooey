#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestButton(glooey.Button): #

    class Label(glooey.Label): #
        custom_text = 'Click me!'
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

def on_click(widget): #
    print(f"{widget} clicked!")

def on_double_click(widget): #
    print(f"{widget} double clicked!")

@run_demos.on_space(gui) #
def test_button():
    button = TestButton()
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "Green button with orange over and purple down states."

    button = TestButton('Custom text!')
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "Different button text."

    button.disable()
    yield "Grey inactive button (no rollover)."
    button.enable()

pyglet.app.run()

