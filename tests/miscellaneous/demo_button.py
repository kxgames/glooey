#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
pyglet.font.add_file('kenvector_future.ttf')
pyglet.font.add_file('kenvector_future_thin.ttf')

root = glooey.Gui(window, batch=batch)
button = glooey.Button('Start Game')
button.label.color = 'white'
button.label.bold = True
button.label.font_name = 'KenVector Future'
button.label.font_size = 12
button.set_base_image(pyglet.image.load('button_green.png'))
button.set_down_image(pyglet.image.load('button_green_down.png'))
button.set_inactive_image(pyglet.image.load('button_grey.png'))

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

