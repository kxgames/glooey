#!/usr/bin/env python3

"""A golden frame should outline a gray box.  Scrolling should change the size 
of the frame and the box."""

import pyglet
import glooey

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.Background(
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
)
root.add(widget)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    root.padding = max(root.padding + scroll_y, 0)


pyglet.app.run()

