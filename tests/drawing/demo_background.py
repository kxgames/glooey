#!/usr/bin/env python3

import pyglet
import glooey
import run_demos
from vecrec import Rect
from pyglet.image import load

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
rect = Rect.from_size(64*8, 64*6)
rect.center = Rect.from_pyglet_window(window).center
bg = glooey.drawing.Background(rect=rect, batch=batch)

@run_demos.on_space(window, batch)
def test_background():
    # Make sure colors can be set, updated, and removed.
    bg.set_appearance(color='green')
    yield "Show a solid green background."

    bg.set_appearance(color='orange')
    yield "Change to a solid orange background."

    # Make sure outlines can be set, updated, and removed.
    bg.set_appearance(outline='green')
    yield "Show a solid green outline."

    bg.set_appearance(outline='orange')
    yield "Change to a solid orange outline."

    # Make sure non-tiled images can be set, updated, and removed.
    bg.image = load('assets/misc/star_5.png')
    yield "Show a green star."

    bg.image = load('assets/misc/star_7.png')
    yield "Change to an orange star."

    # Make sure the center image can be set, updated, and removed.
    bg.set_appearance(center=pyglet.image.load('assets/64x64/green.png'))
    yield "Show a tiled green background."

    bg.set_appearance(center=pyglet.image.load('assets/64x64/orange.png'))
    yield "Change to a tiled orange background."

    # Make sure the side and corner images can bet set, updated, and removed.
    dims = {
            'top': '64x4',
            'right': '4x64',
            'bottom': '64x4',
            'left': '4x64',
            'top_left': '4x4',
            'top_right': '4x4',
            'bottom_right': '4x4',
            'bottom_left': '4x4',
    }
    for side in dims:
        bg.set_appearance(**{
            side: load(f'assets/{dims[side]}/green.png'),
            'htile': True, 'vtile': True
        })
        yield f"Show a green {side.replace('_', ' ')}."

        bg.set_appearance(**{
            side: load(f'assets/{dims[side]}/orange.png'),
            'htile': True, 'vtile': True
        })
        yield f"Change to an orange {side.replace('_', ' ')}."

    # Make sure the background can be hidden and unhidden.
    bg.set_appearance(center=pyglet.image.load('assets/64x64/green.png'))
    yield "Show a tiled green background."

    bg.hide()
    yield "Hide the background."

    bg.show()
    yield "Show the background."

    # Make sure tiling scales with size properly.
    vrect = rect.copy()
    vrect.height -= 96
    vrect.center = rect.center
    bg.rect = vrect
    yield "Squish the rect vertically.  The tiles should remain square."

    hrect = vrect.copy()
    hrect.width -= 96
    hrect.center = rect.center
    bg.rect = hrect
    yield "Squish the rect horizontally.  The tiles should remain square."
    bg.rect = rect

    # Make sure vtile='auto' and htile='auto' work.
    bg.set_appearance(
            top=load('assets/64x4/orange.png'),
            center=load('assets/64x64/green.png'),
            bottom=load('assets/64x4/orange.png'),
    )
    yield "Automatically tile vertically."

    bg.set_appearance(
            left=load('assets/4x64/orange.png'),
            center=load('assets/64x64/green.png'),
            right=load('assets/4x64/orange.png'),
    )
    yield "Automatically tile horizontally."

    bg.set_appearance(
            center=load('assets/64x64/green.png'),
    )
    yield "Automatically tile in both dimensions."

    bg.set_appearance(
            center=load('assets/64x64/green.png'),
            top=load('assets/64x4/orange.png'),
            bottom=load('assets/64x4/orange.png'),
            left=load('assets/4x64/orange.png'),
            right=load('assets/4x64/orange.png'),
            top_left=load('assets/4x4/purple.png'),
            top_right=load('assets/4x4/purple.png'),
            bottom_left=load('assets/4x4/purple.png'),
            bottom_right=load('assets/4x4/purple.png'),
    )
    yield "Automatically tile in both dimensions with a border."

    # Make sure the background can be empty.
    bg.set_appearance()
    yield "Empty the background."


@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

