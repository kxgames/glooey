#!/usr/bin/env python3

import pyglet
import glooey
from pprint import pprint

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

pyglet.font.load('assets/fonts/LiberationMono-Bold.ttf')

class TestButton(glooey.Button):

    class Label(glooey.Label): #
        default_color = '#deeed6'
        default_font_name = 'Liberation Mono'
        default_font_size = 14
        default_bold = True
        default_padding = 100
        #default_padding_horz = 8
        #default_padding_top = 5
        #default_padding_bottom = 2

    default_base_top_left     = pyglet.image.load('assets/button/orange.png')
    default_base_top          = pyglet.image.load('assets/button/orange.png')
    default_base_top_right    = pyglet.image.load('assets/button/orange.png')
    default_base_left         = pyglet.image.load('assets/button/orange.png')
    default_base_center       = pyglet.image.load('assets/button/red.png')
    default_base_right        = pyglet.image.load('assets/button/orange.png')
    default_base_bottom_left  = pyglet.image.load('assets/button/orange.png')
    default_base_bottom       = pyglet.image.load('assets/button/orange.png')
    default_base_bottom_right = pyglet.image.load('assets/button/orange.png')

    default_over_top_left     = pyglet.image.load('assets/button/yellow.png')
    default_over_top          = pyglet.image.load('assets/button/yellow.png')
    default_over_top_right    = pyglet.image.load('assets/button/yellow.png')
    default_over_left         = pyglet.image.load('assets/button/yellow.png')
    default_over_center       = pyglet.image.load('assets/button/green.png')
    default_over_right        = pyglet.image.load('assets/button/yellow.png')
    default_over_bottom_left  = pyglet.image.load('assets/button/yellow.png')
    default_over_bottom       = pyglet.image.load('assets/button/yellow.png')
    default_over_bottom_right = pyglet.image.load('assets/button/yellow.png')

    default_down_top_left     = pyglet.image.load('assets/button/teal.png')
    default_down_top          = pyglet.image.load('assets/button/teal.png')
    default_down_top_right    = pyglet.image.load('assets/button/teal.png')
    default_down_left         = pyglet.image.load('assets/button/teal.png')
    default_down_center       = pyglet.image.load('assets/button/blue.png')
    default_down_right        = pyglet.image.load('assets/button/teal.png')
    default_down_bottom_left  = pyglet.image.load('assets/button/teal.png')
    default_down_bottom       = pyglet.image.load('assets/button/teal.png')
    default_down_bottom_right = pyglet.image.load('assets/button/teal.png')

    default_off_top_left     = pyglet.image.load('assets/button/light_grey.png')
    default_off_top          = pyglet.image.load('assets/button/light_grey.png')
    default_off_top_right    = pyglet.image.load('assets/button/light_grey.png')
    default_off_left         = pyglet.image.load('assets/button/light_grey.png')
    default_off_center       = pyglet.image.load('assets/button/dark_grey.png')
    default_off_right        = pyglet.image.load('assets/button/light_grey.png')
    default_off_bottom_left  = pyglet.image.load('assets/button/light_grey.png')
    default_off_bottom       = pyglet.image.load('assets/button/light_grey.png')
    default_off_bottom_right = pyglet.image.load('assets/button/light_grey.png')

    default_vtile = True
    default_htile = True
    default_alignment = 'center'


root = glooey.Gui(window, batch=batch)
button = TestButton('Hello world!')
root.add(button)

print(button.label.default_padding)
print(button.label.padding)

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

