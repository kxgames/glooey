#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
root = glooey.Gui(window, batch=batch)

button = glooey.Button('Ok')
button.label.color = 'white'
button.label.bold = True
button.base_image = pyglet.image.load('button_square_beige.png')
button.down_image = pyglet.image.load('button_square_beige_pressed.png')
button.inactive_image = pyglet.image.load('button_square_grey.png')

def label_placement(child_rect, parent_rect):   # (no fold)
    child_rect.center = parent_rect.center
    if button.state == 'down':
        child_rect.bottom -= 4

button.label_placement = label_placement

root.add(button, 'center')

@button.event
def on_click(widget):
    print("{} clicked!".format(widget))

@window.event
def on_key_press(symbol, modifier):
    if symbol == pyglet.window.key.SPACE:
        button.active = not button.active


pyglet.app.run()

