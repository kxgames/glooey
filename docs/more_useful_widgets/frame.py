#!/usr/bin/env python3

import glooey
import pyglet

class WesnothFrame(glooey.Frame):

    class Decoration(glooey.Background):
        custom_center = pyglet.resource.texture('center.png')
        custom_top = pyglet.resource.texture('top.png')
        custom_bottom = pyglet.resource.texture('bottom.png')
        custom_left = pyglet.resource.texture('left.png')
        custom_right = pyglet.resource.texture('right.png')
        custom_top_left = pyglet.resource.image('top_left.png')
        custom_top_right = pyglet.resource.image('top_right.png')
        custom_bottom_left = pyglet.resource.image('bottom_left.png')
        custom_bottom_right = pyglet.resource.image('bottom_right.png')

    class Box(glooey.Bin):
        # These paddings are asymmetric because the border images have a
        # 3px shadow on the bottom left side, although you can't see it
        # on a black background.
        custom_right_padding = 14
        custom_top_padding = 14
        custom_left_padding = 17
        custom_bottom_padding = 17

window = pyglet.window.Window()
gui = glooey.Gui(window)

frame = WesnothFrame()
frame.add(glooey.Placeholder(300, 200))
gui.add(frame)

pyglet.app.run()

