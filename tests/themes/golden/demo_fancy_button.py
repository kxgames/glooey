#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
root = golden.Gui(window)
button = golden.FancyButton('lorem ipsum')
root.add(button)

@window.event
def on_key_press(symbol, modifiers):
    global i, j

    if symbol == pyglet.window.key.SPACE:
        i = (i + 1) % len(colors)
        button.set_color(colors[i])

    if symbol == pyglet.window.key.TAB:
        j = (j + 1) % len(icons)
        button.set_icon(icons[j])


pyglet.app.run()


