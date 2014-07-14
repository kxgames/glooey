#!/usr/bin/env python

import pyglet
import glooey
import vecrec

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
rect.shrink(50)

glooey.drawing.draw_rectangle(rect, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
