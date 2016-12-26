#!/usr/bin/env python

"""A green rectangle should take up most of the screen."""

import pyglet
import glooey
import vecrec

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
rect.shrink(50)

glooey.drawing.Rectangle(rect, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
