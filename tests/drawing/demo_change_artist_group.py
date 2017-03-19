#!/usr/bin/env python3

import pyglet
import glooey
import vecrec
import run_demos

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect_1 = vecrec.Rect.from_pyglet_window(window)
rect_1.shrink(50)
rect_2 = rect_1 + (10,-10)

bg = pyglet.graphics.OrderedGroup(0)
fg = pyglet.graphics.OrderedGroup(1)

artist_1 = glooey.drawing.Rectangle(rect_1, color='green', batch=batch)
artist_2 = glooey.drawing.Rectangle(rect_2, color='orange', batch=batch)

@run_demos.on_space(window, batch) #
def test_changing_groups():
    artist_1.group = fg
    artist_2.group = bg
    yield "Green in front."

    artist_1.group = bg
    artist_2.group = fg
    yield "Orange in front."

@window.event #
def on_draw():
    window.clear()
    batch.draw()



pyglet.app.run()

