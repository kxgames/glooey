#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
grid = glooey.Grid()
widgets = { #
        (0,0): glooey.EventLogger(50, 50),
        (0,1): glooey.EventLogger(50, 50),
        (1,0): glooey.EventLogger(50, 50),
        (1,1): glooey.EventLogger(50, 50),
}
gui.add(grid)

@run_demos.on_space(gui) #
def test_grid():
    # Test adding and removing cells.
    for row, col in widgets:
        grid.add(row, col, widgets[row,col])
    assert grid.num_rows == 2
    assert grid.num_cols == 2
    yield "Make a 2x2 grid."

    grid.remove(1, 1)
    assert grid.num_rows == 2
    assert grid.num_cols == 2
    yield "Remove the bottom right cell."

    grid.remove(1, 0)
    assert grid.num_rows == 1
    assert grid.num_cols == 2
    yield "Remove the bottom row."

    grid.clear()
    assert grid.num_rows == 0
    assert grid.num_cols == 0
    yield "Clear the grid."

    for row, col in widgets:
        grid.add(row, col, widgets[row,col])
    assert grid.num_rows == 2
    assert grid.num_cols == 2

    # Test cell padding.
    grid.padding = 10
    yield "Pad the cells by 10px."
    grid.padding = 0

    grid.cell_padding = 10
    yield "Only pad between the cells."
    grid.cell_padding = 0

    # Test cell alignment.
    grid.cell_alignment = 'center'
    yield "Center-align all the cells."
    grid.cell_alignment = 'fill'

    # Test custom row heights/column widths.
    grid.set_row_height(0, 100)
    yield "Make the top row 100 px tall."

    grid.set_row_height(0, 0)
    yield "Make the top row as short as possible (50 px)."

    grid.set_col_width(0, 100)
    yield "Make the left column 100 px wide."

    grid.set_col_width(0, 0)
    yield "Make the left column as narrow as possible (50 px)."
    grid.del_row_height(0)
    grid.del_col_width(0)

    grid.default_row_height = 0
    yield "Make both rows as short as possible."

    grid.default_col_width = 0
    yield "Make both columns as narrow as possible."
    grid.default_row_height = 'expand'
    grid.default_col_width = 'expand'

    # Test custom grid shapes
    grid.num_rows = 3
    assert grid.num_rows == 3
    yield "Make the grid 3x2."

    grid.num_cols = 3
    assert grid.num_cols == 3
    yield "Make the grid 3x3."

    grid.num_rows = 0
    grid.num_cols = 0
    assert grid.num_rows == 2
    assert grid.num_cols == 2


pyglet.app.run()

