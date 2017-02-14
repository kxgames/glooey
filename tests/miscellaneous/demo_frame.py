#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestFrame(glooey.Frame):

    class Background(glooey.Background):
        default_center = pyglet.image.load('assets/4x4/blue.png')
        default_top = pyglet.image.load('assets/4x4/green.png')
        default_bottom = pyglet.image.load('assets/4x4/green.png')
        default_left = pyglet.image.load('assets/4x4/green.png')
        default_right = pyglet.image.load('assets/4x4/green.png')
        default_top_left = pyglet.image.load('assets/4x4/green.png')
        default_top_right = pyglet.image.load('assets/4x4/green.png')
        default_bottom_left = pyglet.image.load('assets/4x4/green.png')
        default_bottom_right = pyglet.image.load('assets/4x4/green.png')
        default_alignment = 'fill'
        default_htile = True
        default_vtile = True

    class Bin(glooey.Bin):
        default_padding = 8



root = glooey.Gui(window, batch=batch)
frame = TestFrame()
widget = glooey.PlaceHolder(color='red')
frame.add(widget)
root.add(frame)

@demo_helpers.interactive_tests(window, batch) #
def test_image():
    yield "A place-holder in a frame."

    frame.padding = 30
    yield "Pad around the frame."

    frame.bin.padding = 38
    yield "Pad inside the frame."

    frame.padding = 0
    frame.bin.padding = 8

pyglet.app.run()

