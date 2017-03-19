#!/usr/bin/env python3

import pyglet
import run_demos
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
frame = golden.SmallFrame()
sub = golden.SubFrame()

frame.add(sub)
gui.add(frame)

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt. Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae. Sed ut justo massa, varius molestie diam. Sed lacus quam, tempor in dictum sed, posuere et diam.'

@run_demos.on_space(gui) #
def test_big_frame():
    sub.clear()
    yield "Empty frame."

    label = golden.Label(lorem_ipsum)
    label.enable_line_wrap(200)
    sub.add(label)
    yield "Frame containing a paragraph."

pyglet.app.run()


