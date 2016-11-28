#!/usr/bin/env python

"""An image of a woman walking should appear in the middle of the screen.  
Scrolling should change the image and create an animation."""

import pyglet
import glooey

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

i = 0
images = [
        pyglet.image.load('green_checkmark.png'),
        pyglet.image.load('green_cross.png'),
]

root = glooey.Gui(window, batch=batch)
widget = glooey.Image(images[i])
root.add(widget, 'center')

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global i
    i = (i - scroll_y) % len(images)
    widget.image = images[i]


pyglet.app.run()

