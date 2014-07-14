#!/usr/bin/env python

import pyglet
import glooey
import vecrec

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

image = pyglet.image.load('tiled-image.png')
rect = vecrec.Rect.from_pyglet_window(window)

glooey.drawing.draw_tiled_image(
        rect, image, horizontal=True, vertical=True, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
