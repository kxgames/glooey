#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos
import itertools

colors = 'blue', 'red', 'green', 'yellow'

window = pyglet.window.Window()
gui = kenney.Gui(window)

buttons = kenney.VBox()
buttons.cell_padding = 8
buttons.add(kenney.YellowButton('Start game'))
buttons.add(kenney.Button('Options'))
buttons.add(kenney.Button('Credits'))

@run_demos.on_space(gui) #
def test_menu():
    # Test the getters and setters for the base button class.
    menu = kenney.Menu("Lorem ipsum")
    menu.add(buttons)
    gui.clear()
    gui.add(menu)

    for color in colors:
        menu.color = color
        yield f"menu.color = {color}"

    menu.clear()

    # Test the pre-configured settings for the named button classes.
    for subcls in kenney.Menu.__subclasses__():
        menu = subcls("Lorem ipsum")
        menu.add(buttons)
        gui.clear()
        gui.add(menu)
        yield subcls.__name__
        menu.clear()

pyglet.app.run()


