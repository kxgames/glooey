#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
widget = glooey.Placeholder(50, 50)

# Added padding to this test, because doing so revealed a bug in the alignment 
# code.  See #21.
widget.padding = 25

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
@run_demos.on_space(gui) #
def test_alignment():
    gui.clear()
    gui.add(widget)
    for test in alignments:
        widget.alignment = test
        yield f"alignment = '{test}'"

    for test in alignments:
        custom_widget_cls = type('TestWidget', (glooey.Placeholder,), {
            'custom_alignment':
                test if isinstance(test, str) else staticmethod(test),
        })
        custom_widget = custom_widget_cls(50, 50)
        custom_widget.color = 'orange'
        custom_widget.padding = 25

        gui.clear()
        gui.add(custom_widget)
        yield f"custom_alignment = '{test}'"


pyglet.app.run()

