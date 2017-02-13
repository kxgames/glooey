#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden
import demo_helpers

window = pyglet.window.Window()
root = golden.Gui(window)
bar = golden.BasicFillBar()
bar.alignment = 'center'
root.add(bar)

@demo_helpers.interactive_tests(window, root.batch) #
def test_basic_fill_bar():
    colors = 'red', 'yellow', 'lime', 'green', 'teal', 'blue'
    fractions = [i/10 for i in range(11)]

    for color in colors:
        bar.color = color
        for frac in fractions:
            bar.fraction_filled = frac
            yield f"{int(100 * bar.fraction_filled)}% filled."

pyglet.app.run()
