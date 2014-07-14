#!/usr/bin/env python

import pyglet
import glooey
import vecrec

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
edge = pyglet.image.load('frame-edge.png')
corner = pyglet.image.load('frame-corner.png')

glooey.drawing.draw_frame(rect, edge, 'top', corner, 'top left', batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
