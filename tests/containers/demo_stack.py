#!/usr/bin/env python3

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

    for widget in stack:
        if widget.is_under_mouse(x, y):
            break
    else:
        return

    if button == pyglet.window.mouse.RIGHT:
        stack.remove(widget)


demo_helpers.install_padding_hotkeys(window, stack)
demo_helpers.install_placement_hotkeys(window, stack)

pyglet.app.run()

