#!/usr/bin/env python3

import pyglet
import glooey
import vecrec

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rects = glooey.drawing.make_grid(
        rect=vecrec.Rect.from_pyglet_window(window),
        num_rows=2,
        num_cols=2,
        padding=40,
)
bg1 = glooey.drawing.Background(
        rect=rects[0,0],
        color=glooey.drawing.Color.from_hex('#847e87'),
        batch=batch,
)
bg2 = glooey.drawing.Background(
        rect=rects[0,1],
        center=pyglet.image.load('frame_center.png'),
        vtile=True,
        htile=True,
        batch=batch,
)
bg3 = glooey.drawing.Background(
        rect=rects[1,0],
        left=pyglet.image.load('header_left.png'),
        center=pyglet.image.load('header_center.png'),
        right=pyglet.image.load('header_right.png'),
        htile=True,
        batch=batch,
)
bg4 = glooey.drawing.Background(
        rect=rects[1,1],
        center=pyglet.image.load('frame_center.png'),
        left=pyglet.image.load('frame_left.png'),
        right=pyglet.image.load('frame_right.png'),
        top=pyglet.image.load('frame_top.png'),
        bottom=pyglet.image.load('frame_bottom.png'),
        top_left=pyglet.image.load('frame_top_left.png'),
        top_right=pyglet.image.load('frame_top_right.png'),
        bottom_left=pyglet.image.load('frame_bottom_left.png'),
        bottom_right=pyglet.image.load('frame_bottom_right.png'),
        vtile=True,
        htile=True,
        batch=batch,
)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

