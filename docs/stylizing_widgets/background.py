#!/usr/bin/env python3

import glooey
import pyglet

class WesnothBorder(glooey.Background):
    custom_center = pyglet.resource.texture('center.png')
    custom_top = pyglet.resource.texture('top.png')
    custom_bottom = pyglet.resource.texture('bottom.png')
    custom_left = pyglet.resource.texture('left.png')
    custom_right = pyglet.resource.texture('right.png')
    custom_top_left = pyglet.resource.image('top_left.png')
    custom_top_right = pyglet.resource.image('top_right.png')
    custom_bottom_left = pyglet.resource.image('bottom_left.png')
    custom_bottom_right = pyglet.resource.image('bottom_right.png')

window = pyglet.window.Window()
gui = glooey.Gui(window)

border = WesnothBorder()
gui.add(border)

pyglet.app.run()

