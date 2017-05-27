#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos

colors = 'grey', 'blue', 'red', 'green', 'yellow'

window = pyglet.window.Window()
gui = kenney.Gui(window)
label = kenney.Label(kenney.drawing.lorem_ipsum(5), 300)

@run_demos.on_space(gui) #
def test_frame():
    # Test the setters for the base frame class.
    frame = kenney.Frame()
    frame.add(label)

    gui.clear()
    gui.add(frame)

    for color in colors:
        frame.color = color
        yield f"{color} frame."

    # Test the pre-configured settings for the named frame classes.
    for subcls in kenney.Frame.__subclasses__():
        frame.clear()
        frame = subcls()
        frame.add(label)

        gui.clear()
        gui.add(frame)

        yield f"{subcls.__name__}"

    frame.clear()

pyglet.app.run()


