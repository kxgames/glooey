#!/usr/bin/env python3

import pyglet
import glooey
from pprint import pprint

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

pyglet.font.load('assets/fonts/LiberationMono-Bold.ttf')

class TestButton(glooey.Button):
    default_vtile = True
    default_htile = True
    default_alignment = 'center'

    class Label(glooey.Label):
        default_color = '#deeed6'
        default_font_name = 'Liberation Mono'
        default_font_size = 14
        default_bold = True
        default_padding = 100
        #default_horz_padding_horz = 8
        #default_top_padding_top = 5
        #default_bottom_padding = 2

    class Base(glooey.Background):
        default_top_left     = pyglet.image.load('assets/button/orange.png')
        default_top          = pyglet.image.load('assets/button/orange.png')
        default_top_right    = pyglet.image.load('assets/button/orange.png')
        default_left         = pyglet.image.load('assets/button/orange.png')
        default_center       = pyglet.image.load('assets/button/red.png')
        default_right        = pyglet.image.load('assets/button/orange.png')
        default_bottom_left  = pyglet.image.load('assets/button/orange.png')
        default_bottom       = pyglet.image.load('assets/button/orange.png')
        default_bottom_right = pyglet.image.load('assets/button/orange.png')

    class Over(glooey.Background):
        default_top_left     = pyglet.image.load('assets/button/yellow.png')
        default_top          = pyglet.image.load('assets/button/yellow.png')
        default_top_right    = pyglet.image.load('assets/button/yellow.png')
        default_left         = pyglet.image.load('assets/button/yellow.png')
        default_center       = pyglet.image.load('assets/button/green.png')
        default_right        = pyglet.image.load('assets/button/yellow.png')
        default_bottom_left  = pyglet.image.load('assets/button/yellow.png')
        default_bottom       = pyglet.image.load('assets/button/yellow.png')
        default_bottom_right = pyglet.image.load('assets/button/yellow.png')

    class Down(glooey.Background):
        default_top_left     = pyglet.image.load('assets/button/teal.png')
        default_top          = pyglet.image.load('assets/button/teal.png')
        default_top_right    = pyglet.image.load('assets/button/teal.png')
        default_left         = pyglet.image.load('assets/button/teal.png')
        default_center       = pyglet.image.load('assets/button/blue.png')
        default_right        = pyglet.image.load('assets/button/teal.png')
        default_bottom_left  = pyglet.image.load('assets/button/teal.png')
        default_bottom       = pyglet.image.load('assets/button/teal.png')
        default_bottom_right = pyglet.image.load('assets/button/teal.png')

    class Off(glooey.Background):
        default_top_left     = pyglet.image.load('assets/button/light_grey.png')
        default_top          = pyglet.image.load('assets/button/light_grey.png')
        default_top_right    = pyglet.image.load('assets/button/light_grey.png')
        default_left         = pyglet.image.load('assets/button/light_grey.png')
        default_center       = pyglet.image.load('assets/button/dark_grey.png')
        default_right        = pyglet.image.load('assets/button/light_grey.png')
        default_bottom_left  = pyglet.image.load('assets/button/light_grey.png')
        default_bottom       = pyglet.image.load('assets/button/light_grey.png')
        default_bottom_right = pyglet.image.load('assets/button/light_grey.png')



root = glooey.Gui(window, batch=batch)
button = TestButton('Hello world!')
root.add(button)

@button.event
def on_click(widget):
    print("{} clicked!".format(widget))

@button.event
def on_double_click(widget):
    print("{} double clicked!".format(widget))

@window.event
def on_key_press(symbol, modifier):
    if symbol == pyglet.window.key.SPACE:
        if button.is_active:
            button.deactivate()
        else:
            button.reactivate()


pyglet.app.run()

