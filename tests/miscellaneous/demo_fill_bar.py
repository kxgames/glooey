#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestFillBar(glooey.FillBar):
    default_alignment = 'fill horz'

    class Base(glooey.Background):
        default_left = pyglet.image.load('assets/4x24/blue.png')
        default_center = pyglet.image.load('assets/4x24/green.png')
        default_right = pyglet.image.load('assets/4x24/blue.png')
        default_htile = True

    class Fill(glooey.Background):
        default_center = pyglet.image.load('assets/4x24/red.png')
        default_horz_padding = 4
        default_htile = True

root = glooey.Gui(window, batch=batch)
bar = TestFillBar()
root.add(bar)

@demo_helpers.interactive_tests(window, batch) #
def test_image():
    global bar

    # Make sure the default parameters work as expected.
    for i in range(11):
        bar.fraction_filled = i / 10
        yield f"{int(100 * bar.fraction_filled)}% red."

    # Make sure the images can be changed after initialization.
    bar.base.set_images(
        left=pyglet.image.load('assets/4x24/red.png'),
        center=pyglet.image.load('assets/4x24/blue.png'),
        right=pyglet.image.load('assets/4x24/red.png'),
        htile=True,
    )
    bar.fill.set_images(
        center=pyglet.image.load('assets/4x24/green.png'),
        htile=True,
    )
    for i in range(11):
        bar.fraction_filled = i / 10
        yield f"{int(100 * bar.fraction_filled)}% green."

    # Reset the test.
    bar = TestFillBar()
    root.add(bar)


pyglet.app.run()
