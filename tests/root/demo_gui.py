#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
w, h = window.width, window.height

gui = glooey.Gui(window)
logger = glooey.EventLogger(0.8 * w, 0.8 * h, align='center')
gui.add(logger)

@demo_helpers.interactive_tests(window, gui.batch) #
def test_gui():
    gui.set_cursor(pyglet.image.load('assets/misc/cursor_flipped.png'), (16, 0))
    yield "Use a cursor with a bottom-right hotspot."
    gui.set_cursor(pyglet.image.load('assets/misc/cursor.png'), (0, 16))

    popup = glooey.EventLogger(0.2 * w, 0.2 * h, color='orange', align='center')
    gui.add(popup)
    yield "Mouse events should preferentially go to the pop-up."
    gui.remove(popup)


pyglet.app.run()


