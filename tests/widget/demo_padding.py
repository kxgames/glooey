#!/usr/bin/env python3

"""\
A place-holder widget should take up the whole window.  Press space repeatedly
to iterate through a number of different padding configurations.  The first
four configurations pad just one side (in the order: left, right, top, bottom).
The next two configurations set horizontal and vertical padding, respectively.
The final configuration sets the same padding on every side."""


import pyglet
import glooey

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.PlaceHolder()
root.add(widget)

i = 0
@window.event
def on_key_press(symbol, modifiers): #
    if symbol == pyglet.window.key.SPACE:
        global i

        if i == 0:
            widget.set_padding(left=100)
        if i == 1:
            widget.set_padding(right=100)
        if i == 2:
            widget.set_padding(top=100)
        if i == 3:
            widget.set_padding(bottom=100)
        if i == 4:
            widget.set_padding(horz=100)
        if i == 5:
            widget.set_padding(vert=100)
        if i == 6:
            widget.padding = 100

        i = (i + 1) % 7

pyglet.app.run()


