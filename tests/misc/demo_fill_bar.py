#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestFillBar(glooey.FillBar): #
    custom_alignment = 'fill horz'
    custom_padding = 100

    class Base(glooey.Background): #
        custom_left = pyglet.image.load('assets/4x64/purple.png')
        custom_center = pyglet.image.load('assets/64x64/grey.png')
        custom_right = pyglet.image.load('assets/4x64/purple.png')

    class Fill(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/green.png')
        custom_horz_padding = 4

window = pyglet.window.Window()
gui = glooey.Gui(window)
bar = TestFillBar()
gui.add(bar)

@run_demos.on_space(gui) #
def test_fill_bar():
    global bar
    steps = 5

    # Make sure the default parameters work as expected.
    for i in range(steps + 1):
        bar.fraction_filled = i / steps
        yield f"{int(100 * bar.fraction_filled)}% green."

    # Make sure the images can be changed after initialization.
    bar.base.set_appearance(
        left=pyglet.image.load('assets/4x64/purple.png'),
        center=pyglet.image.load('assets/64x64/grey.png'),
        right=pyglet.image.load('assets/4x64/purple.png'),
        htile=True,
    )
    bar.fill.set_appearance(
        center=pyglet.image.load('assets/64x64/orange.png'),
        htile=True,
    )
    for i in range(steps + 1):
        bar.fraction_filled = i / steps
        yield f"{int(100 * bar.fraction_filled)}% orange."

    # Reset the test.
    bar = TestFillBar()
    gui.add(bar)


pyglet.app.run()
