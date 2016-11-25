#!/usr/bin/env python

import pyglet
import glooey
import vecrec

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
dx, r = 100, 40

glooey.drawing.draw_circle(rect.center + (dx, 0), r, batch=batch)
glooey.drawing.draw_circle(rect.center +  (0, 0), r, batch=batch)
glooey.drawing.draw_circle(rect.center - (dx, 0), r, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()
    cb = pyglet.image.get_buffer_manager().get_color_buffer()
    cb.save('screenshot.png')


pyglet.app.run()
