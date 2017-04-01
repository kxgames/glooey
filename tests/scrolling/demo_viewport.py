#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
cursor = pyglet.image.load('assets/misc/cursor.png')
hotspot = 4, 24

class TestContent(glooey.Grid):
    """
    A 5x5 grid of event loggers.
    """
    custom_num_rows = 5
    custom_num_cols = 5
    custom_padding = 50

    def __init__(self):
        super().__init__()

        for i in range(5):
            for j in range(5):
                self.add(i, j, glooey.Placeholder(150, 150))

        self.add(2, 2, glooey.EventLogger(150, 150, 'orange'))



gui = glooey.PanningGui(window, cursor, hotspot)
viewport = glooey.Viewport()
content = TestContent()

viewport.add(content)
gui.add(viewport)

viewport.center_of_view = content[2,2].rect.center

pyglet.app.run()

