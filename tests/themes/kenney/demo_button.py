#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos
import itertools

colors = 'blue', 'red', 'green', 'yellow', 'grey'
glosses = 'high', 'low', 'matte'

window = pyglet.window.Window()
gui = kenney.Gui(window)

@run_demos.on_space(gui) #
def test_button():
    # Test the getters and setters for the base button class.
    button = kenney.Button('Lorem ipsum')
    gui.clear()
    gui.add(button)

    for color, gloss in itertools.product(colors, glosses):
        button.color = color
        button.gloss = gloss
        yield f"{color}, {gloss} gloss button."

    # Test the pre-configured settings for the named button classes.
    for subcls in kenney.Button.__subclasses__():
        gui.clear()
        gui.add(subcls("Lorem ipsum"))
        yield subcls.__name__

pyglet.app.run()


