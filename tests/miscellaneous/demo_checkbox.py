#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
button = glooey.Checkbox(
        checked_base=pyglet.image.load('checkbox_green_checked.png'),
        checked_over=pyglet.image.load('checkbox_green_checked_over.png'),
        checked_off=pyglet.image.load('checkbox_inactive_checked.png'),
        unchecked_base=pyglet.image.load('checkbox_unchecked.png'),
        unchecked_over=pyglet.image.load('checkbox_green_unchecked_over.png'),
        unchecked_off=pyglet.image.load('checkbox_inactive_unchecked.png'),
)
root.add(button, 'center')

@button.event
def on_toggle(widget):
    print(f"{widget} is {'checked' if widget.is_checked else 'unchecked'}!")

@window.event
def on_key_press(symbol, modifier):
    if symbol == pyglet.window.key.SPACE:
        button.deactivate() if button.is_active else button.reactivate()

pyglet.app.run()

