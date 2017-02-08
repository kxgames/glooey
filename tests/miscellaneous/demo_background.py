#!/usr/bin/env python3

"""A golden frame should outline a gray box.  Scrolling should change the size 
of the frame and the box."""

import pyglet
import glooey
import demo_helpers

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
assets = glooey.themes.ResourceLoader('test')

root = glooey.Gui(window, batch=batch)
bg = glooey.Background(
        center=pyglet.image.load('assets/frame/center.png'),
        left=pyglet.image.load('assets/frame/left.png'),
        right=pyglet.image.load('assets/frame/right.png'),
        top=pyglet.image.load('assets/frame/top.png'),
        bottom=pyglet.image.load('assets/frame/bottom.png'),
        top_left=pyglet.image.load('assets/frame/top_left.png'),
        top_right=pyglet.image.load('assets/frame/top_right.png'),
        bottom_left=pyglet.image.load('assets/frame/bottom_left.png'),
        bottom_right=pyglet.image.load('assets/frame/bottom_right.png'),
        vtile=True,
        htile=True,
)
root.add(bg)

@demo_helpers.interactive_tests(window, batch)
def test_background():
    #bg.set_images(color=glooey.drawing.colors['red'])
    #yield "Make the background red."

    bg.padding = 100
    yield

    bg.padding = 200
    yield "padding = 200"

    bg.padding = 100
    yield "padding = 100"

    # Not right...
    bg.alignment = 'center'
    print(bg.claimed_rect)
    yield "alignment = 'center'"

    bg.alignment = 'fill'
    yield "alignment = 'fill'"



@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    root.padding = max(root.padding - scroll_y, 0)


pyglet.app.run()

