#!/usr/bin/env python

"""The screen should begin with 5 horizontally stacked boxes and the following 
hotkeys should have the following effects:

u: Add a red box to the left side of the screen.
i: Add an orange box to the middle of the screen.
o: Add a yellow box to the right side of the screen.

If you hold <Ctrl>, the box will be given 100 px of space.
If you hold <Shift>, the box will be given as little space as possible.
If you hold neither, the box will expand to fill any available space.

left click: replace the box you clicked on with one of a different color.
right click: remove the box you clicked on.

q,w,e,a,s,d,f,z,x,c: Change the placement algorithm.
j,k: Change the padding
"""

import pyglet
import demo_helpers
from glooey import *
from glooey.drawing import *
from pprint import pprint

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
hbox = HBox(padding=4)
for i in range(5):
    hbox.add(PlaceHolder(20, 20, color=green))
root.add(hbox)

@window.event
def on_key_press(symbol, modifiers):
    from pyglet.window import key

    size = 100 if modifiers & key.MOD_CTRL else None
    size = 0 if modifiers & key.MOD_SHIFT else size
    placement = 'fill' if size is not None else None

    if symbol == key.U:
        widget = PlaceHolder(20, 20, color=red)
        hbox.add_front(widget, size, placement)

    if symbol == key.I:
        i = len(hbox) // 2
        widget = PlaceHolder(20, 20, color=orange)
        hbox.insert(widget, i, size, placement)

    if symbol == key.O:
        widget = PlaceHolder(20, 20, color=yellow)
        hbox.add_back(widget, size, placement)

@window.event
def on_mouse_press(x, y, button, modifiers):
    from pyglet.window import key

    for widget in hbox:
        if widget.is_under_mouse(x, y):
            break
    else:
        return

    if button == pyglet.window.mouse.LEFT:
        color = blue if widget.color == green else green
        new_widget = PlaceHolder(20, 20, color=color)
        hbox.replace(widget, new_widget)

    if button == pyglet.window.mouse.RIGHT:
        hbox.remove(widget)


demo_helpers.install_padding_hotkeys(window, hbox)
demo_helpers.install_placement_hotkeys(window, hbox)

pyglet.app.run()


