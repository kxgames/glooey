#!/usr/bin/env python3

"""\
"""

import pyglet
import glooey.themes.golden as golden

print(__doc__)

i, j = 0, 0
colors = 'red', 'green', 'blue', 'grey'
icons = None, 'save', 'chat', 'zoom', 'yes', 'no', 'plus', 'minus', 'up', 'right', 'down', 'left'

window = pyglet.window.Window()
root = golden.Gui(window)
button = golden.RoundButton(colors[i], icons[j])
root.add(button, 'center')

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


