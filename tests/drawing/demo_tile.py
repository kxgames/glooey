#!/usr/bin/env python3

import pyglet
import glooey
import run_demos
from vecrec import Vector, Rect

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rects = { #
        'big': Rect.from_size(64*8, 64*6),
        'small': Rect.from_size(64*4, 64*3),
}
images = { #
        'green': pyglet.image.load('assets/64x64/green.png'),
        'orange': pyglet.image.load('assets/64x64/orange.png'),
}

window_rect = Rect.from_pyglet_window(window)
for rect in rects.values():
    rect.center = window_rect.center

artist = glooey.drawing.Tile(
        rects['big'], images['green'], vtile=True, htile=True, batch=batch)

@run_demos.on_space(window, batch)
def test_tile():
    yield "Show a green pattern."
    artist.image = images['orange']
    yield "Change to an orange pattern."
    artist.image = images['green']

    artist.rect = rects['small']
    yield "Make the rect smaller."
    artist.rect = rects['big']

    artist.htile = False
    yield "Don't tile horizontally."
    artist.htile = True
    artist.vtile = False
    yield "Don't tile vertically."
    artist.htile = False
    yield "Don't tile at all."
    artist.htile = True
    artist.vtile = True

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

