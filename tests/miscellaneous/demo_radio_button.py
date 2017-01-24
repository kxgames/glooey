#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
hbox = glooey.HBox(padding=5, placement='center')

images = dict(
        checked_base=pyglet.image.load('checkbox_green_checked.png'),
        checked_over=pyglet.image.load('checkbox_green_checked_over.png'),
        unchecked_base=pyglet.image.load('checkbox_unchecked.png'),
        unchecked_over=pyglet.image.load('checkbox_green_unchecked_over.png'),
)
def on_toggle(widget):
    print(f"{widget}: {widget.is_checked}")

buttons = []
for i in range(3):
    button = glooey.RadioButton(buttons, **images)
    button.push_handlers(on_toggle=on_toggle)
    hbox.add(button)

root.add(hbox, 'center')

pyglet.app.run()

