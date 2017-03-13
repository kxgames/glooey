#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestFrame(glooey.Frame): #
    custom_alignment = 'fill'

    class Decoration(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/green.png')

    class Bin(glooey.Bin): #
        custom_padding = 16

class TestBackground(glooey.Background): #
    custom_center = pyglet.image.load('assets/64x64/orange.png')

gui = glooey.Gui(window, batch=batch)
frame = TestFrame()
widget = TestBackground()
frame.add(widget)
gui.add(frame)

@demo_helpers.interactive_tests(window, batch) #
def test_image():
    yield "A orange tiled background in green tiled frame."

    frame.padding = 32
    yield "Pad around the frame."

    frame.bin.padding = 48
    yield "Pad inside the frame."

    frame.padding = 0
    frame.bin.padding = 16

pyglet.app.run()

