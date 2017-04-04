#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos
import itertools

colors = 'blue', 'red', 'green', 'yellow', 'grey'

window = pyglet.window.Window()
gui = kenney.Gui(window)

@run_demos.on_space(gui) #
def test_radio_button():
    # Test the getters and setters for the base button class.
    button = kenney.RadioButton()
    gui.clear()
    gui.add(button)

    for color in colors:
        button.color = color
        yield f"{color}"

    # Test the pre-configured settings for the named button classes.
    # 
    # Note that when one radio button is switched for another (as in this 
    # test), you have to move the mouse to trigger an on_mouse_enter() event 
    # before you can click on the widget.  This is necessary because the GUI 
    # doesn't keep track of where the mouse is, and I decided that fixing this 
    # would introduce more complexity than its worth.
    for subcls in kenney.RadioButton.__subclasses__():
        gui.clear()
        gui.add(subcls())
        yield subcls.__name__

pyglet.app.run()


