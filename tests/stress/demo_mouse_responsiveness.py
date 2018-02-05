#!/usr/bin/env python3

"""\
Test how smoothly mouse events are handled by a large number of widgets.

This demo fills the screen with a grid of 4x4 px widgets that change color in 
response to rollover events.  The test is to see how responsive the widgets 
are.

Note that these color-changing widgets are custom-written to be simple and 
performant.  If this test were to use Button widgets instead, it would be a 
lot less responsive because Button has a lot more repacking and regrouping 
overhead in order to be flexible.  Since filling up a screen like this is not 
the intended use-case for buttons, I think it's fair to use a custom-written 
widget that allows mouse-responsiveness to come to the forefront.

It is important to note that this test uses a Grid to organize the widgets, and 
Grid uses a custom algorithm to detect mouse events.  The default algorithm (as 
implemented in Widget) involves an O(N) search for children that are under the 
mouse.  Grid instead searches for the row under the mouse, then for the column 
under the mouse, which is effectively O(√N).  That said, this layout is totally 
flat, and a "real" GUI would probably be much more hierarchical.  In that case, 
the search for widgets under the mouse would probably approach O(log(N))."""


import pyglet
import glooey
from pprint import pprint

print(__doc__)

UNIT = 5

class TestButton(glooey.Widget):

    def __init__(self):
        super().__init__()
        self.rectangle = None

    def do_claim(self):
        return UNIT, UNIT

    def _draw(self):
        if self.rectangle is None:
            self.rectangle = glooey.drawing.Rectangle(
                    rect=self.rect,
                    color='green',
                    batch=self.batch,
                    group=self.group,
                    usage='dynamic',
            )
        else:
            self.rectangle.show()

    def _undraw(self):
        if self.rectangle is not None:
            self.rectangle.hide()

    def on_rollover(self, widget, new_state, old_state):
        if new_state == 'base':
            self.rectangle.color = 'green'
        if new_state == 'over':
            self.rectangle.color = 'orange'
        if new_state == 'down':
            self.rectangle.color = 'purple'



window = pyglet.window.Window()
gui = glooey.Gui(window)
grid = glooey.Grid()

print()
for i in range(window.height // UNIT):
    for j in range(window.width // UNIT):
        grid.add(i, j, TestButton())
        print(f"\rAdding row [{i+1}/{window.height // UNIT}]", end='')

cursor = pyglet.image.load('assets/misc/cursor_green_circle.png')
hotspot = 8, 8

gui.set_cursor(cursor, hotspot)
gui.add(grid)

pyglet.app.run()

