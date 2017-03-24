#!/usr/bin/env python3

import pyglet
import glooey
import run_demos
from vecrec import Vector, Rect

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

full = Rect.from_pyglet_window(window)
left = Rect(full.left, full.bottom, full.width/2, full.height)
right = Rect(full.left, full.bottom, full.width/2, full.height)
right.left = left.right
left.shrink(50)
right.shrink(50)


@run_demos.on_space(window, batch)
def test_outline():
    a = glooey.drawing.Outline(left, batch=batch)
    b = glooey.drawing.Outline(right, batch=batch)
    yield "Show two unconnected outlines."
    a.hide()
    b.hide()

    c = glooey.drawing.Outline(full, batch=batch)
    yield "Put an outline just inside the window."
    c.hide()

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()
