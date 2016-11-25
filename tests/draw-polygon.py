#!/usr/bin/env python

import pyglet
import glooey
import vecrec
import math

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
dx, r = 100, 40

def draw_pentagon(center, radius):
    from_degrees = vecrec.Vector.from_degrees
    vertices = [
            center + radius * from_degrees(360 * i / 5)
            for i in range(5)
    ]
    glooey.drawing.draw_convex_polygon(vertices, batch=batch)


draw_pentagon(rect.center + (dx, 0), r)
draw_pentagon(rect.center +  (0, 0), r)
draw_pentagon(rect.center - (dx, 0), r)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
