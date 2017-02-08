#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.PlaceHolder(200, 200)
root.add(widget)

alignments = [ #
        'fill',
        'top left', 'top', 'top right', 
        'left', 'center', 'right',
        'bottom left', 'bottom', 'bottom right',
]
@demo_helpers.interactive_tests(window, batch) #
def interactive_padding_tests():
    for test in alignments:
        widget.alignment = test
        yield f"alignment = '{test}'"


pyglet.app.run()

