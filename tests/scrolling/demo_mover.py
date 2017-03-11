#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
gui = glooey.Gui(window)
mover = glooey.Mover()
frame = glooey.Outline()
widget = glooey.EventLogger(50, 50, 'orange')

mover.size_hint = 200, 200
mover.alignment = 'center'

frame.add(mover)
gui.add(frame)

# Test changing children.

@demo_helpers.interactive_tests(window, gui.batch) #
def interactive_mover_tests():
    # Test the initial position.
    
    mover.clear()
    mover.initial_position = 'center'
    mover.add(widget)
    yield "Initially position the widget in the center."

    mover.clear()
    mover.initial_position = 'bottom'
    mover.add(widget)
    yield "Initially position the widget on the bottom."

    mover.clear()
    mover.initial_position = 'top'
    mover.add(widget)
    yield "Initially position the widget on the top."

    mover.clear()
    mover.initial_position = 150, 75
    mover.add(widget)
    yield "Initially position the widget on the right."

    mover.clear()
    mover.initial_position = 0, 75
    mover.add(widget)
    yield "Initially position the widget on the left."

    # Test panning by distance.

    mover.pan(0, -25)
    yield "Pan down 25 px."

    mover.pan(0, -1000)
    yield "Pan down as far as possible."

    mover.pan(25, 0)
    yield "Pan right 25 px."

    mover.pan(1000, 0)
    yield "Pan right as far as possible."

    mover.pan(0, 25)
    yield "Pan up 25 px."

    mover.pan(0, 1000)
    yield "Pan up as far as possible."

    mover.pan(-25, 0)
    yield "Pan left 25 px."

    mover.pan(-1000, 0)
    yield "Pan left as far as possible."

    # Test panning by percent.

    mover.pan_percent(0, -0.5)
    yield "Pan halfway to the bottom."

    mover.pan_percent(0, -1.0)
    yield "Pan all the way to the bottom."

    mover.pan_percent(0.5, 0)
    yield "Pan halfway to the right."

    mover.pan_percent(1.0, 0)
    yield "Pan all the way to the right."

    mover.pan_percent(0, 0.5)
    yield "Pan halfway to the top."

    mover.pan_percent(0, 1.0)
    yield "Pan all the way to the top."

    mover.pan_percent(-0.5, 0)
    yield "Pan halfway to the left."

    mover.pan_percent(-1.0, 0)
    yield "Pan all the way to the left."

    # Test jumping by alignment.

    mover.jump('center')
    yield "Jump to the center."

    mover.jump('bottom right')
    yield "Jump to the bottom-right corner."
    
    mover.jump('top left')
    yield "Jump to the top-left corner."

    mover.jump('top right')
    yield "Jump to the top-right corner."

    mover.jump('bottom left')
    yield "Jump to the bottom-left corner."

    # Test jumping by distance.

    mover.jump(140, 10)
    yield "Jump near the bottom-right corner."

    mover.jump(1000, -1000)
    yield "Jump past the bottom-right corner."

    mover.jump(10, 140)
    yield "Jump to the top-left corner."

    mover.jump(-1000, 1000)
    yield "Jump past the top-left corner."

    mover.jump(140, 140)
    yield "Jump to the top-right corner."

    mover.jump(1000, 1000)
    yield "Jump past the top-right corner."

    mover.jump(10, 10)
    yield "Jump to the bottom-left corner."

    mover.jump(-1000, -1000)
    yield "Jump past the bottom-left corner."

    # Test jumping by percent.

    mover.jump_percent(0.5, 0.5)
    yield "Jump to the center."

    mover.jump_percent(0.95, 0.5)
    yield "Jump near the right edge."

    mover.jump_percent(10.0, 0.5)
    yield "Jump past the right edge."

    mover.jump_percent(0.05, 0.5)
    yield "Jump near the left edge."

    mover.jump_percent(-10.0, 0.5)
    yield "Jump past the left edge."

    mover.jump_percent(0.5, 0.95)
    yield "Jump near the top edge."

    mover.jump_percent(0.5, 10.0)
    yield "Jump past the top edge."

    mover.jump_percent(0.5, 0.05)
    yield "Jump near the bottom edge."

    mover.jump_percent(0.5, -10.0)
    yield "Jump past the bottom edge."


pyglet.app.run()



