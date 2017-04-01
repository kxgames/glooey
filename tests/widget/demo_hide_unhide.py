#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
hbox = glooey.HBox()
hbox.padding = 30
first = glooey.Placeholder()
second = glooey.Placeholder()
hbox.add(first)
hbox.add(second)
gui.add(hbox)

@run_demos.on_space(gui) #
def test_padding():
    yield "Show both widgets."

    first.hide()
    yield "Hide the first widget."

    first.unhide()
    second.hide()
    yield "Hide the second widget."

    hbox.hide()
    yield "Hide the hbox."

    third = glooey.Placeholder()
    hbox.add(third)
    yield "Add a third widget to the hbox, but don't show it."

    hbox.unhide()
    yield "Unhide the hbox, keep hiding the second widget."

    hbox.remove(third)
    yield "Remove the third widget from the hbox."

    second.unhide()

pyglet.app.run()


