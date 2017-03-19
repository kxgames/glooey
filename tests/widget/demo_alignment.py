#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

gui = glooey.Gui(window, batch=batch)
widget = glooey.PlaceHolder(200, 200)

def left_half(rect, boundary): #
    rect.width = boundary.width / 2
    rect.height = boundary.height
    rect.top_left = boundary.top_left

def right_half(rect, boundary): #
    rect.width = boundary.width / 2
    rect.height = boundary.height
    rect.top_right = boundary.top_right

alignments = [ #
        'fill', 'fill horz', 'fill vert',
        'fill top', 'fill bottom', 'fill left', 'fill right',
        'top left', 'top', 'top right', 
        'left', 'center', 'right',
        'bottom left', 'bottom', 'bottom right',
        left_half, right_half,
]
@demo_helpers.interactive_tests(window, batch) #
def interactive_padding_tests():
    gui.add(widget)
    for test in alignments:
        widget.alignment = test
        yield f"alignment = '{test}'"

    for test in alignments:
        custom_widget_cls = type('TestWidget', (glooey.PlaceHolder,), {
            'custom_alignment':
                test if isinstance(test, str) else staticmethod(test),
        })
        gui.clear()
        gui.add(custom_widget_cls(200, 200))
        yield f"custom_alignment = '{test}'"


pyglet.app.run()

