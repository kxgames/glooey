#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestBackground(glooey.Background): #
    default_center = pyglet.image.load('assets/64x64/green.png')
    default_top = pyglet.image.load('assets/64x4/orange.png')
    default_bottom = pyglet.image.load('assets/64x4/orange.png')
    default_left = pyglet.image.load('assets/4x64/orange.png')
    default_right = pyglet.image.load('assets/4x64/orange.png')
    default_top_left = pyglet.image.load('assets/4x4/purple.png')
    default_top_right = pyglet.image.load('assets/4x4/purple.png')
    default_bottom_left = pyglet.image.load('assets/4x4/purple.png')
    default_bottom_right = pyglet.image.load('assets/4x4/purple.png')

root = glooey.Gui(window, batch=batch)
bg = TestBackground()
root.add(bg)

@demo_helpers.interactive_tests(window, batch) #
def test_background():
    yield "Show a green background with orange sides and purple corners."

    bg.padding = 200
    yield "Increase the padding to 200px."
    bg.padding = 0

    bg.alignment = 'center'
    yield "Center-align the background."
    bg.alignment = 'fill'

pyglet.app.run()

