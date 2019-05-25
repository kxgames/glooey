#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestScrollContent(glooey.Grid):
    """
    A 2x2 grid of event loggers that is 450x450 px.
    """
    custom_num_rows = 2
    custom_num_cols = 2
    custom_padding = 50

    def __init__(self):
        super().__init__()

        for i in range(2):
            for j in range(2):
                self.add(i, j, glooey.EventLogger(150, 150, 'orange'))

class TestScrollPane(glooey.ScrollPane):
    custom_vert_scrolling = True
    custom_horz_scrolling = True

class TestHVScrollBar:

    class Decoration(glooey.Background):
        custom_color = 'dark'

    class Forward(glooey.Button):
        custom_size_hint = 20, 20
        custom_alignment = 'fill'
        custom_base_color = 'green'
        custom_over_color = 'orange'
        custom_down_color = 'purple'

    class Backward(glooey.Button):
        custom_size_hint = 20, 20
        custom_alignment = 'fill'
        custom_base_color = 'green'
        custom_over_color = 'orange'
        custom_down_color = 'purple'

    class Grip(glooey.Button):
        custom_size_hint = 20, 20
        custom_alignment = 'fill'
        custom_base_color = 'green'
        custom_over_color = 'orange'
        custom_down_color = 'purple'

class TestHScrollBar(TestHVScrollBar, glooey.HScrollBar):
    pass

class TestVScrollBar(TestHVScrollBar, glooey.VScrollBar):
    pass

window = pyglet.window.Window()
gui = glooey.Gui(window)
grid = glooey.Grid(2, 2)

frame = glooey.Frame()
pane = TestScrollPane()
hbar = TestHScrollBar(pane)
vbar = TestVScrollBar(pane)
big_content = TestScrollContent()
small_content = glooey.Placeholder(100, 100)

grid.size_hint = 200, 200
grid.padding = 10
grid.set_row_height(1, 0)
grid.set_col_width(1, 0)
grid.alignment = 'center'
frame.alignment = 'fill'
frame.decoration.outline = 'green'

pane.add(big_content)
frame.add(pane)
grid.add(0, 0, frame)
grid.add(0, 1, vbar)
grid.add(1, 0, hbar)
gui.add(grid)

@run_demos.on_space(gui)
def interactive_mover_tests():
    vbar.scale_grip = False
    hbar.scale_grip = False
    #yield "Horizontal and vertical scroll bars."

    pane.add(small_content)
    yield "Content smaller than the pane."
    pane.add(big_content)
    
    vbar.scale_grip = True
    hbar.scale_grip = True
    yield "Scaled scroll grips."

    pane.add(small_content)
    yield "Scaled scroll grips with content smaller than the pane."
    pane.add(big_content)

pyglet.app.run()



