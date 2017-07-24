#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

grid = glooey.Grid(2, 2)
grid.padding = 10

grid.add(0, 0, glooey.Placeholder())
grid.add(0, 1, glooey.Placeholder())
grid.add(1, 0, glooey.Placeholder())
grid.add(1, 1, glooey.Placeholder())

gui.add(grid)

pyglet.app.run()
