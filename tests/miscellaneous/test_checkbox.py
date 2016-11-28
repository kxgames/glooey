#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
button = glooey.Checkbox()
button.base_checked_image = pyglet.image.load('checkbox_green_checked.png')
button.over_checked_image = pyglet.image.load('checkbox_green_checked_over.png')
button.base_unchecked_image = pyglet.image.load('checkbox_unchecked.png')
button.over_unchecked_image = pyglet.image.load('checkbox_green_unchecked_over.png')
root.add(button, 'center')

@button.event
def on_toggle(widget):
    print("{} is {}!".format(widget, "on" if widget.is_checked else "off"))

@window.event
def on_key_press(symbol, modifier):
    if symbol == pyglet.window.key.SPACE:
        button.deactivate() if button.is_active else button.reactivate()


pyglet.app.run()

