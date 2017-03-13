#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

gui = glooey.Gui(window, batch=batch)
logger = glooey.EventLogger()
logger.padding = 100
gui.add(logger)

@demo_helpers.interactive_tests(window, batch) #
def test_gui():
    gui.set_cursor(pyglet.image.load('cursor_nw.png'), (0, 16))
    yield "Use a cursor with a top-left hotspot."

    gui.set_cursor(pyglet.image.load('cursor_se.png'), (16, 0))
    yield "Use a cursor with a bottom-right hotspot."

pyglet.app.run()


