#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
widget = glooey.PlaceHolder(200, 200)
root.add(widget)

def left_half(rect, boundry): #
    rect.width = boundry.width / 2
    rect.height = boundry.height
    rect.top_left = boundry.top_left

def top_left_quarter(rect, boundry): #
    rect.width = boundry.width / 2
    rect.height = boundry.height / 2
    rect.top_left = boundry.top_left

alignments = [ #
        'fill', 'fill horz', 'fill vert',
        'fill top', 'fill bottom', 'fill left', 'fill right',
        'top left', 'top', 'top right', 
        'left', 'center', 'right',
        'bottom left', 'bottom', 'bottom right',
        left_half, top_left_quarter,
]
@demo_helpers.interactive_tests(window, batch) #
def interactive_padding_tests():
    for test in alignments:
        widget.alignment = test
        yield f"alignment = '{test}'"


pyglet.app.run()

