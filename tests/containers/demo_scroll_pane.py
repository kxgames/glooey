#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
gui = glooey.Gui(window)

pane = glooey.ScrollPane()
pane.size_hint = 300, 300
pane.horz_scrolling = True
pane.vert_scrolling = True
pane.alignment = 'center'

frame = glooey.Frame()
frame.background.color = 'dark'

grid = glooey.Grid(2, 2)
grid.padding = 50
for i in range(2):
    for j in range(2):
        grid.add(i, j, glooey.EventLogger(150, 150))

frame.add(grid)
pane.add(frame)
gui.add(pane)

@demo_helpers.interactive_tests(window, gui.batch) #
def interactive_bin_tests():
    yield "Clip a 2x2 grid of placeholders."

    # Test scrolling by distance.

    pane.scroll(0, -25)
    yield "Scroll down half a padding-height (25 px)."

    pane.scroll(0, -1000)
    yield "Scroll down as far as possible."

    pane.scroll(25, 0)
    yield "Scroll right half a padding-width (25 px)."

    pane.scroll(1000, 0)
    yield "Scroll right as far as possible."

    pane.scroll(0, 25)
    yield "Scroll up half a padding-height (25 px)."

    pane.scroll(0, 1000)
    yield "Scroll up as far as possible."

    pane.scroll(-25, 0)
    yield "Scroll left half a padding-width (25 px)."

    pane.scroll(-1000, 0)
    yield "Scroll left as far as possible."

    # Test scrolling by percent.

    pane.scroll_percent(0, -0.5)
    yield "Scroll halfway to the bottom."

    pane.scroll_percent(0, -1.0)
    yield "Scroll down as far as possible."

    pane.scroll_percent(0.5, 0)
    yield "Scroll halfway to the right."

    pane.scroll_percent(1.0, 0)
    yield "Scroll right as far as possible."

    pane.scroll_percent(0, 0.5)
    yield "Scroll halfway to the top."

    pane.scroll_percent(0, 1.0)
    yield "Scroll up as far as possible."

    pane.scroll_percent(-0.5, 0)
    yield "Scroll halfway to the left."

    pane.scroll_percent(-1.0, 0)
    yield "Scroll left as far as possible."

    # Test jumping by distance.

    pane.jump(75, 75)
    yield "Jump to the center."

    pane.jump(150, 0)
    yield "Jump to the bottom-right corner."

    pane.jump(0, 150)
    yield "Jump to the top-left corner."

    pane.jump(150, 150)
    yield "Jump to the top-right corner."

    pane.jump(0, 0)
    yield "Jump to the bottom-left corner."

    # Test jumping by percent.

    pane.jump_percent(0.5, 0.5)
    yield "Jump to the center."

    pane.jump_percent(1.0, 0.5)
    yield "Jump to the center of the right edge."

    pane.jump_percent(0, 0.5)
    yield "Jump to the center of the left edge."

    pane.jump_percent(0.5, 1.0)
    yield "Jump to the center of the top edge."

    pane.jump_percent(0.5, 0)
    yield "Jump to the center of the bottom edge."
    pane.jump(0, 0)

    # Test setting which dimensions can scroll.

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

    # Test setting the view using alignment functions.
    
    pane.view = 'center'
    yield "Show the center."

    pane.view = 'left'
    yield "Show the center of the left edge."

    pane.view = 'bottom left'
    yield "Show the bottom left corner."

    pane.view = 'bottom'
    yield "Show the center of the bottom edge."

    pane.view = 'bottom right'
    yield "Show the bottom right corner."

    pane.view = 'right'
    yield "Show the center of the right edge."

    pane.view = 'top right'
    yield "Show the top right corner."

    pane.view = 'top'
    yield "Show the center of the top edge."

    pane.view = 'top left'

pyglet.app.run()



