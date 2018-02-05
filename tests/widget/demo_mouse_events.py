#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class EventLoggerLabel(glooey.Label):
    custom_alignment = 'center'
    custom_color = 'green'

    def __init__(self, logger):
        super().__init__(str(logger))



window = pyglet.window.Window()
gui = glooey.Gui(window)
grid = glooey.Grid(2, 2)
grid.padding = 50
grid.cell_padding = 50
grid.set_row_height(0, 0)

loggers = [ #
        glooey.EventLogger(),
        glooey.EventLogger(),
]

grid[0,0] = EventLoggerLabel(loggers[0])
grid[1,0] = loggers[0]
grid[0,1] = EventLoggerLabel(loggers[1])
grid[1,1] = loggers[1]

gui.add(grid)

@run_demos.on_space(gui) #
def test_mouse_events():
    yield "Move the mouse and make sure the correct events are printed."

    loggers[0]._grab_mouse()
    yield f"{loggers[0]} should print every event."
    loggers[0]._ungrab_mouse()

    loggers[1]._grab_mouse()
    yield f"{loggers[1]} should print every event."

    loggers[1].hide()
    yield f"Hiding {loggers[1]} should ungrab the mouse."
    loggers[1].unhide()

pyglet.app.run()


