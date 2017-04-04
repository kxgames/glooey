#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos
import itertools

colors = 'blue', 'red', 'green', 'yellow', 'grey'
icons = 'cross', 'checkmark'

window = pyglet.window.Window()
gui = kenney.Gui(window)

def on_click(widget): #
    print(f"{widget} was clicked!")

@run_demos.on_space(gui) #
def test_round_button():
    # Test the getters and setters for the base button class.
    button = kenney.RoundButton()
    button.push_handlers(on_click)
    gui.clear()
    gui.add(button)

    for color, icon in itertools.product(colors, icons):
        button.color = color
        button.icon = icon
        yield f"{color} button with {icon}."
        del button.image

        button.text = '+'
        yield f"{color} button with '+' sign."
        del button.text

    # Test the pre-configured settings for the named button classes.
    for subcls in kenney.RoundButton.__subclasses__():
        button = subcls()
        button.push_handlers(on_click)
        gui.clear()
        gui.add(button)
        yield subcls.__name__

pyglet.app.run()


