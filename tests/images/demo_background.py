#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestBackground(glooey.Background): #
    custom_center = pyglet.image.load('assets/64x64/green.png')
    custom_top = pyglet.image.load('assets/64x4/orange.png')
    custom_bottom = pyglet.image.load('assets/64x4/orange.png')
    custom_left = pyglet.image.load('assets/4x64/orange.png')
    custom_right = pyglet.image.load('assets/4x64/orange.png')
    custom_top_left = pyglet.image.load('assets/4x4/purple.png')
    custom_top_right = pyglet.image.load('assets/4x4/purple.png')
    custom_bottom_left = pyglet.image.load('assets/4x4/purple.png')
    custom_bottom_right = pyglet.image.load('assets/4x4/purple.png')

gui = glooey.Gui(window, batch=batch)
bg = TestBackground()
gui.add(bg)

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

