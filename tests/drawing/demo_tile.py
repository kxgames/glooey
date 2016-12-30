#!/usr/bin/env python3

"""Brown floor tiles should take up most (but not all) of the screen.

h: toggle horizontal tiling
v: toggle vertical tiling
left click: change the color of the tiles.
scroll: change the size of the floor area."""

import pyglet
import glooey
import vecrec

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

rect = vecrec.Rect.from_pyglet_window(window)
rect.shrink(50)
images = [
        pyglet.image.load('tile_brown.png'),
        pyglet.image.load('tile_teal.png'),
]
artist = glooey.drawing.Tile(
        rect, images[0], vtile=True, htile=True, batch=batch)

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    i = images.index(artist.image)
    artist.image = images[(i+1) % len(images)]

@window.event
def on_mouse_scroll(x, y, dx, dy):
    artist.rect = artist.rect.get_grown(5*dy)

@window.event
def on_key_press(symbol, modifier):
    from pyglet.window import key

    if symbol == key.H:
        artist.htile = not artist.htile
    if symbol == key.V:
        artist.vtile = not artist.vtile


pyglet.app.run()

