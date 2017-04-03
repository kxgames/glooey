#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos
import itertools

colors = 'blue', 'red', 'green', 'yellow', 'grey'
icons = 'checkmark', 'cross'

window = pyglet.window.Window()
gui = kenney.Gui(window)

@run_demos.on_space(gui) #
def test_checkbox():
    # Test the getters and setters for the base button class.
    button = kenney.Checkbox()
    gui.clear()
    gui.add(button)

    for color, icon in itertools.product(colors, icons):
        button.color = color
        button.icon = icon
        yield f"{color}, {icon}"

    # Test the pre-configured settings for the named button classes.  Note that 
    # when one checkbox is switched for another (as in this test), you have to 
    # move the mouse to trigger an on_mouse_enter() event before you can click 
    # on the widget.  This is necessary because the GUI doesn't keep track of 
    # where the mouse is, and I decided that fixing this would introduce more 
    # complexity than its worth.
    for subcls in kenney.Checkbox.__subclasses__():
        gui.clear()
        gui.add(subcls())
        yield subcls.__name__




pyglet.app.run()


