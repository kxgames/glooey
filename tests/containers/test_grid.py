#!/usr/bin/env python

"""A 5x5 grid of placeholders should be displayed."""

import pyglet
import test_helpers
from glooey import *
from glooey.drawing import *

print(__doc__)

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
grid = Grid(5, 5, padding=5)

for row, col in grid.yield_cells():
    grid[row, col] = PlaceHolder(30, 30, color=rainbow_cycle[row])

root.add(grid)

test_helpers.install_padding_hotkeys(window, grid)
test_helpers.install_placement_hotkeys(window, grid)

pyglet.app.run()


