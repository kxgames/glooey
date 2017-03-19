#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden
import run_demos

colors = 'red', 'green', 'blue', 'grey'
icons = None, 'save', 'chat', 'zoom', 'yes', 'no', 'plus', 'minus', 'up', 'right', 'down', 'left'

window = pyglet.window.Window()
gui = golden.Gui(window)
button = golden.RoundButton()
gui.add(button)

@run_demos.on_space(gui) #
def test_round_button():
    for color in colors:
        button.color = color
        for icon in icons:
            button.icon = icon
            yield f"{color} button with {icon or 'no'} icon."


pyglet.app.run()


