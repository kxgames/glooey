#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
mover = glooey.Mover()
frame = glooey.Frame()
frame.decoration.outline = 'green'

mover.size_hint = 200, 200
mover.alignment = 'center'

frame.add(mover)
gui.add(frame)

@run_demos.on_space(gui)
def interactive_mover_tests():
    unpadded = glooey.EventLogger(50, 50, 'orange')
    padded = glooey.EventLogger(10, 10, 'purple')
    padded.padding = 20

    for widget in unpadded, padded:
        widget.alignment = 'top right'
        mover.add(widget)
        yield f"Add the {'padded' if widget is padded else 'unpadded'} widget to the top right corner of the mover."

        # Test panning by distance.

        mover.pan(-25, 0)
        yield "Pan left 25 px."

        mover.pan(-1000, 0)
        yield "Pan past the left edge."

        mover.pan(0, -25)
        yield "Pan down 25 px."

        mover.pan(0, -1000)
        yield "Pan past the bottom edge."

        mover.pan(25, 0)
        yield "Pan right 25 px."

        mover.pan(1000, 0)
        yield "Pan past the right edge."

        mover.pan(0, 25)
        yield "Pan up 25 px."

        mover.pan(0, 1000)
        yield "Pan past the top edge."

        # Test panning by percent.

        mover.pan_percent(-0.5, 0)
        yield "Pan 50% to the left."

        mover.pan_percent(-1.0, 0)
        yield "Pan past the left edge."

        mover.pan_percent(0, -0.5)
        yield "Pan 50% to the bottom."

        mover.pan_percent(0, -1.0)
        yield "Pan past the bottom edge."

        mover.pan_percent(0.5, 0)
        yield "Pan 50% to the right."

        mover.pan_percent(10.0, 0)
        yield "Pan past the right edge."

        mover.pan_percent(0, 0.5)
        yield "Pan 50% to the top."

        mover.pan_percent(0, 1.0)
        yield "Pan past the top edge."

        # Test jumping by distance.

        mover.jump(75, 75)
        yield "Jump to the center."

        mover.jump(10, 10)
        yield "Jump 10 px from the bottom-left corner."

        mover.jump(-1000, -1000)
        yield "Jump past the bottom-left corner."

        mover.jump(140, 140)
        yield "Jump 10 px from the top-right corner."

        mover.jump(1000, 1000)
        yield "Jump past the top-right corner."

        mover.jump(140, 10)
        yield "Jump 10 px from the bottom-right corner."

        mover.jump(1000, -1000)
        yield "Jump past the bottom-right corner."

        mover.jump(10, 140)
        yield "Jump 10 px from the top-left corner."

        mover.jump(-1000, 1000)
        yield "Jump past the top-left corner."

        # Test jumping by percent.

        mover.jump_percent(0.5, 0.5)
        yield "Jump to the center."

        mover.jump_percent(0.9, 0.5)
        yield "Jump 90% of the way to the right edge."

        mover.jump_percent(10.0, 0.5)
        yield "Jump past the right edge."

        mover.jump_percent(0.1, 0.5)
        yield "Jump 90% of the way to the left edge."

        mover.jump_percent(-10.0, 0.5)
        yield "Jump past the left edge."

        mover.jump_percent(0.5, 0.9)
        yield "Jump 90% of the way to the top edge."

        mover.jump_percent(0.5, 10.0)
        yield "Jump past the top edge."

        mover.jump_percent(0.5, 0.1)
        yield "Jump 90% of the way to the bottom edge."

        mover.jump_percent(0.5, -10.0)
        yield "Jump past the bottom edge."


pyglet.app.run()



