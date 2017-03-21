#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)

frame = glooey.Frame()
frame.decoration.outline = 'green'

pane = glooey.ScrollPane()
pane.size_hint = 300, 300
pane.horz_scrolling = True
pane.vert_scrolling = True

grid = glooey.Grid(2, 2)  # 450×450
grid.padding = 50
for i in range(2):
    for j in range(2):
        grid.add(i, j, glooey.EventLogger(150, 150, 'orange'))

frame.add(pane)
gui.add(frame)

@run_demos.on_space(gui) #
def interactive_bin_tests():
    pane.add(grid)
    yield "Clip a 2x2 grid of placeholders."

    ## Test setting the view.
    
    pane.view = 'left'
    yield "view = 'left'"

    pane.view = 'bottom left'
    yield "view = 'bottom left'"

    pane.view = 'bottom'
    yield "view = 'bottom'"

    pane.view = 'bottom right'
    yield "view = 'bottom right'"

    pane.view = 'right'
    yield "view = 'right'"

    pane.view = 'top right'
    yield "view = 'top right'"

    pane.view = 'top'
    yield "view = 'top'"

    pane.view = 'top left'
    yield "view = 'top left'"

    pane.view = 'center'
    yield "view = 'center'"

    ## Test setting the initial view.

    pane.initial_view = 'top left'
    yield "Setting initial view doesn't change anything..."

    pane.add(grid)
    yield "...until a new widget is added."
    
    ## Test scrolling by distance.

    pane.view = 'top left'
    pane.scroll(0, -25)
    yield "Scroll 25 px down."

    pane.scroll(0, -1000)
    yield "Scroll past the bottom edge."

    pane.scroll(25, 0)
    yield "Scroll 25 px right."

    pane.scroll(1000, 0)
    yield "Scroll past the right edge."

    pane.scroll(0, 25)
    yield "Scroll 25 px up."

    pane.scroll(0, 1000)
    yield "Scroll past the top edge."

    pane.scroll(-25, 0)
    yield "Scroll 25 px left."

    pane.scroll(-1000, 0)
    yield "Scroll past the left edge."

    ## Test scrolling by percent.

    pane.scroll_percent(0, -0.5)
    yield "Scroll 50% to the bottom."

    pane.scroll_percent(0, -10.0)
    yield "Scroll past the bottom edge."

    pane.scroll_percent(0.5, 0)
    yield "Scroll 50% to the right."

    pane.scroll_percent(10.0, 0)
    yield "Scroll past the right edge."

    pane.scroll_percent(0, 0.5)
    yield "Scroll 50% to the top."

    pane.scroll_percent(0, 10.0)
    yield "Scroll past the top edge."

    pane.scroll_percent(-0.5, 0)
    yield "Scroll 50% to the left."

    pane.scroll_percent(-10.0, 0)
    yield "Scroll past the left edge."

    ## Test jumping by distance.

    pane.jump(75, 75)
    yield "Jump to the center."

    pane.jump(125, 125)
    yield "Jump 25 px from the top-right corner."

    pane.jump(2500, 2500)
    yield "Jump past the top-right corner."

    pane.jump(25, 25)
    yield "Jump 25 px from the bottom-left corner."

    pane.jump(-2500, -2500)
    yield "Jump past the bottom-left corner."

    pane.jump(125, 25)
    yield "Jump 25 px from the bottom-right corner."

    pane.jump(2500, -2500)
    yield "Jump past the bottom-right corner."

    pane.jump(25, 125)
    yield "Jump 25 px from the top-left corner."

    pane.jump(-2500, 2500)
    yield "Jump past the top-left corner."

    ## Test jumping by percent.

    pane.jump_percent(0.5, 0.5)
    yield "Jump to the center."

    pane.jump_percent(0.9, 0.5)
    yield "Jump 90% of the way to the right edge."

    pane.jump_percent(10.0, 0.5)
    yield "Jump past the right edge."

    pane.jump_percent(0.1, 0.5)
    yield "Jump 90% of the way to the left edge."

    pane.jump_percent(-10.0, 0.5)
    yield "Jump past the left edge."

    pane.jump_percent(0.5, 0.9)
    yield "Jump 90% of the way to the top edge."

    pane.jump_percent(0.5, 10.0)
    yield "Jump past the top edge."

    pane.jump_percent(0.5, 0.1)
    yield "Jump 90% of the way to the bottom edge."

    pane.jump_percent(0.5, -10.0)
    yield "Jump past the bottom edge."

    ## Test setting which dimensions can scroll.

    pane.jump(0, 0)
    pane.horz_scrolling = False
    yield "Show the full width of the grid."

    pane.scroll_percent(1, 1)
    yield "Scroll vertically but not horizontally."

    pane.horz_scrolling = True
    pane.jump(0, 0)

    pane.vert_scrolling = False
    yield "Show the full height of the grid."

    pane.scroll_percent(1, 1)
    yield "Scroll horizontally but not vertically."

    pane.vert_scrolling = True


pyglet.app.run()



