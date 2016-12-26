#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
hbox = glooey.HBox(padding=5, placement='center')

buttons = []
for i in range(3):
    button = glooey.RadioButton(buttons)
    hbox.add(button)

    button.i = i
    button.base_checked_image = pyglet.image.load('checkbox_green_checked.png')
    button.over_checked_image = pyglet.image.load('checkbox_green_checked_over.png')
    button.base_unchecked_image = pyglet.image.load('checkbox_unchecked.png')
    button.over_unchecked_image = pyglet.image.load('checkbox_green_unchecked_over.png')
    button.push_handlers(on_toggle=lambda widget: print(
        "RadioButton #{} is {}".format(widget.i, widget.is_checked)))

    buttons.append(button)

root.add(hbox, 'center')

pyglet.app.run()

