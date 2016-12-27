#!/usr/bin/env python

"""A 5x5 grid of placeholders should be displayed.  The first row and column 
should take as little space as possible, while the remaining rows and columns 
should fill the available space evenly.  The following hotkeys should have the 
following effects:

q,w,e,a,s,d,f,z,x,c: Change the placement algorithm.
j,k: Change the padding
"""

import pyglet
import demo_helpers
import glooey
import glooey.drawing

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
grid = glooey.Grid(padding=5)
grid.set_row_height(0, 0)
grid.set_col_width(0, 0)

for row in range(5):
    for col in range(5):
        color = glooey.drawing.rainbow_cycle[row]
        placement = 'fill' if row == col else None
        widget = glooey.PlaceHolder(30, 30, color=color)
        grid.add(row, col, widget, placement=placement)

root.add(grid)

demo_helpers.install_padding_hotkeys(window, grid)
demo_helpers.install_placement_hotkeys(window, grid)

pyglet.app.run()


