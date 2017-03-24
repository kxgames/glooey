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


class TestScrollBox(glooey.ScrollBox):

    class Frame(glooey.Frame):

        class Decoration(glooey.Background):
            custom_outline = 'green'

    class Corner(glooey.Frame):
        custom_alignment = 'fill'

        class Decoration(glooey.Background):
            custom_outline = 'green'

    class HVBar(glooey.HVScrollBar):

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

        class Grip(glooey.HVScrollBar.Grip):
            custom_size_hint = 20, 20

            class Base(glooey.Background):
                custom_color = 'green'

            class Over(glooey.Background):
                custom_color = 'orange'

            class Down(glooey.Background):
                custom_color = 'purple'

    class HBar(HVBar):
        HVBox = glooey.HBox

    class VBar(HVBar):
        HVBox = glooey.VBox



window = pyglet.window.Window()
gui = glooey.Gui(window)
box = TestScrollBox()
content = TestScrollContent()

box.size_hint = 200, 200
box.alignment = 'center'

box.add(content)
gui.add(box)

pyglet.app.run()



