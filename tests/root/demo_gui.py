#!/usr/bin/env python3

"""\
The window should just be black, but the cursor should be a gold triangle.
"""

import pyglet
import glooey

print(__doc__)

window = pyglet.window.Window()
root = glooey.Gui(window)
root.add(glooey.EventLogger(), padding=100)

cursor = 0
cursors = [
        (pyglet.image.load('cursor_nw.png'), (0, 16)),
        (pyglet.image.load('cursor_se.png'), (16, 0)),
]

root.set_cursor(*cursors[cursor])

@window.event
def on_mouse_release(*args):
    global cursor
    cursor = (cursor + 1) % len(cursors)
    root.set_cursor(*cursors[cursor])

pyglet.app.run()


