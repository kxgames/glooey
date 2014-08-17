#!/usr/bin/env python

import pyglet
from glooey import *
from glooey.drawing import *
from itertools import product

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
grid = Grid(5, 5, padding=5)

for row, col in grid.yield_cells():
    grid[row, col] = PlaceHolder(color=rainbow_cycle[row])

root.add(grid)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()


