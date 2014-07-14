#!/usr/bin/env python

import pyglet
import glooey
import vecrec

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
image = pyglet.image.load('swirly-image.png')

rect = vecrec.Rect.from_pyglet_image(image)
rect.center_x = window.width / 2
rect.center_y = window.height / 2

glooey.drawing.draw_image(rect, image, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
