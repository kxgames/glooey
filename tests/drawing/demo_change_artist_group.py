#!/usr/bin/env python3

"""An orange rectangle should be displayed on top of a green one.  When you 
click with the mouse, the green rectangle should move on top.  When you release 
the mouse, the orange rectangle should move back to the top."""

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
    print('(draw)')
    window.clear()
    batch.draw()

@window.event
def on_mouse_press(self, *args):
    print("- green in front")
    artist_1.group = fg
    artist_2.group = bg

@window.event
def on_mouse_release(self, *args):
    print("- orange in front")
    artist_1.group = bg
    artist_2.group = fg


pyglet.app.run()

