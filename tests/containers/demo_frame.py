#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestFrame(glooey.Frame): #
    custom_alignment = 'fill'

    class Decoration(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/green.png')

    class Box(glooey.Bin): #
        custom_padding = 16

class TestBackground(glooey.Background): #
    custom_center = pyglet.image.load('assets/64x64/orange.png')

window = pyglet.window.Window()
gui = glooey.Gui(window)

@run_demos.on_space(gui) #
def test_image():
    frame = TestFrame()
    widget = TestBackground()
    frame.add(widget)
    gui.add(frame)
    yield "A orange tiled background in green tiled frame."

    frame.padding = 32
    yield "Pad around the frame."

    frame.box.padding = 48
    yield "Pad inside the frame."

    bg = glooey.Background()
    bg.set_appearance(center=pyglet.image.load('assets/64x64/purple.png'))
    frame.decoration = bg
    yield "Dynamically change the background."

pyglet.app.run()

