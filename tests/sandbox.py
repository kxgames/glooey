#!/usr/bin/env python

import pyglet

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

batch.add(
        3, pyglet.gl.GL_LINE_STRIP, None,
        ('v2f', (10, 10, 50, 100, 90, 10)))

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

