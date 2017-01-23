#!/usr/bin/env python3

import pyglet
import glooey
from pprint import pprint

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
pyglet.font.add_file('kenvector_future.ttf')
pyglet.font.add_file('kenvector_future_thin.ttf')

root = glooey.Gui(window, batch=batch)
button = glooey.Button()

def label_placement(child_rect, parent_rect):   # (no fold)
    child_rect.center = parent_rect.center
    if button.rollover == 'down':
        child_rect.bottom -= 4

button.set_text(
        text='Start Game!',
        color='white',
        bold='True',
        font_name = 'KenVector Future',
        font_size = 12,
        placement=label_placement,
)
button.set_background_images(
        base=pyglet.image.load('button_green.png'),
        down=pyglet.image.load('button_green_down.png'),
        off=pyglet.image.load('button_grey.png'),
)
button.repack_on_rollover = True

root.add(button, 'center')

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

