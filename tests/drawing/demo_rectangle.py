#!/usr/bin/env python3

"""Two green rectangles should take up most of the screen."""

import pyglet
import glooey
import vecrec

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

full = vecrec.Rect.from_pyglet_window(window)
left = vecrec.Rect(full.left, full.bottom, full.width/2, full.height)
right = vecrec.Rect(full.left, full.bottom, full.width/2, full.height)
right.left = left.right
left.shrink(50)
right.shrink(50)

glooey.drawing.Rectangle(left, batch=batch)
glooey.drawing.Rectangle(right, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
