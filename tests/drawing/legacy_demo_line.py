#!/usr/bin/env python

import pyglet
import glooey
import vecrec
import math

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
w, h, dy = 200, 25, 100

def draw_chevron(center, width, height):
    vertices = []
    vertices.append(center + (-width / 2, height))
    vertices.append(center)
    vertices.append(center + (width / 2, height))

    glooey.drawing.draw_line(vertices, batch=batch)


draw_chevron(rect.center + (0, dy), w, h)
draw_chevron(rect.center + (0, 0), w, h)
draw_chevron(rect.center + (0, -dy), w, h)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
