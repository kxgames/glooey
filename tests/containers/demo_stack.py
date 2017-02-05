#!/usr/bin/env python3

"""\
There should be 5 place-holders, of decreasing size and sorted in the order of 
the rainbow.  The test is to make sure that the place-holders are properly 
sorted along the z-axis.

right click: Remove the widget under the mouse.
q,w,e,a,s,d,f,z,x,c: Change the placement algorithm.
j,k: Change the padding"""

import pyglet
import demo_helpers
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
stack = Stack()
stack.placement = 'center'

def percent(percent):
    def placement(child_rect, parent_rect):
        child_rect.width = percent * parent_rect.width / 100
        child_rect.height = percent * parent_rect.height / 100
        cast_to_placement_function(stack.placement)(child_rect, parent_rect)
    return placement

stack.add(PlaceHolder(0, 0, color=blue), placement=percent(100))
stack.add(PlaceHolder(0, 0, color=green), placement=percent(80))
stack.add(PlaceHolder(0, 0, color=yellow), placement=percent(60))
stack.add(PlaceHolder(0, 0, color=orange), placement=percent(40))
stack.add(PlaceHolder(0, 0, color=red), placement=percent(20))

root.add(stack)

@window.event
def on_mouse_press(x, y, button, modifiers):
    from pyglet.window import key

    if button == pyglet.window.mouse.RIGHT:
        # Need to use for-else because it's a run-time error to change the size 
        # of a container (Widget.__children here) while iterating over it.
        for widget in stack:
            if widget.is_under_mouse(x, y):
                break
        else:
            return

        stack.remove(widget)


demo_helpers.install_placement_hotkeys(window, stack)

print(__doc__)

pyglet.app.run()

