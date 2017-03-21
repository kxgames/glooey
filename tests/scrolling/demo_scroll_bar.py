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

class TestHVScrollBar(glooey.HVScrollBar):

    class Decoration(glooey.Background):
        custom_color = 'dark'

    class Forward(glooey.Button):
        custom_size_hint = 20, 20

        class Base(glooey.Background):
            custom_color = 'green'

        class Over(glooey.Background):
            custom_color = 'orange'

        class Down(glooey.Background):
            custom_color = 'purple'

    class Backward(glooey.Button):
        custom_size_hint = 20, 20

        class Base(glooey.Background):
            custom_color = 'green'

        class Over(glooey.Background):
            custom_color = 'orange'

        class Down(glooey.Background):
            custom_color = 'purple'

    class Grip(glooey.VScrollBar.Grip):
        custom_size_hint = 20, 20

        class Base(glooey.Background):
            custom_color = 'green'

        class Over(glooey.Background):
            custom_color = 'orange'

        class Down(glooey.Background):
            custom_color = 'purple'


class TestHScrollBar(TestHVScrollBar):
    HVBox = glooey.HBox

class TestVScrollBar(TestHVScrollBar):
    HVBox = glooey.VBox


window = pyglet.window.Window()
gui = glooey.Gui(window)
grid = glooey.Grid(2, 2)

frame = glooey.Frame()
pane = TestScrollPane()
hbar = TestHScrollBar(pane)
vbar = TestVScrollBar(pane)
content = TestScrollContent()

grid.size_hint = 200, 200
grid.padding = 10
grid.set_row_height(1, 0)
grid.set_col_width(1, 0)
grid.alignment = 'center'
frame.alignment = 'fill'
frame.decoration.outline = 'green'

pane.add(content)
frame.add(pane)
grid.add(0, 0, frame)
grid.add(0, 1, vbar)
grid.add(1, 0, hbar)
gui.add(grid)

pyglet.app.run()



