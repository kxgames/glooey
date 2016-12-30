#!/usr/bin/env python3

"""Two overlapping rectangles should appear.  The orange one should be on top.

left mouse press: Move the green rectangle on top.
left mouse release: Move the orange rectangle back on top."""

import pyglet
import glooey
import vecrec
from glooey.drawing import green, orange

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect_1 = vecrec.Rect.from_pyglet_window(window)
rect_1.shrink(50)
rect_2 = rect_1 + (10,-10)

bg = pyglet.graphics.OrderedGroup(0)
fg = pyglet.graphics.OrderedGroup(1)

artist_1 = glooey.drawing.Rectangle(rect_1, color=green, batch=batch, group=bg)
artist_2 = glooey.drawing.Rectangle(rect_2, color=orange, batch=batch, group=fg)

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_mouse_press(self, *args):
    artist_1.group = fg
    artist_2.group = bg

@window.event
def on_mouse_release(self, *args):
    artist_1.group = bg
    artist_2.group = fg


pyglet.app.run()

