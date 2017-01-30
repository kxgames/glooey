#!/usr/bin/env python3

import pyglet
import glooey
from pprint import pprint

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
theme = glooey.themes.ResourceLoader('wesnoth')
theme.add_font('fonts/Lato-Regular.ttf')

class WesnothButton(glooey.Button):

    class Label(glooey.Label): #
        default_color = '#b9ad86'
        default_font_name = 'Lato Regular'
        default_font_size = 10

    default_base = theme.image('buttons/button_normal/button_H22.png')
    default_over = theme.image('buttons/button_normal/button_H22-active.png')
    default_down = theme.image('buttons/button_normal/button_H22-pressed.png')
    default_label_placement = 'center'


root = glooey.Gui(window, batch=batch)
vbox = glooey.VBox()
button = WesnothButton('Tutorial')
vbox.add(button, placement='center')
root.add(vbox)

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
            print('deactivate')
            button.deactivate()
        else:
            print('reactivate')
            button.reactivate()
        print(button.is_active)
        print()


pyglet.app.run()

