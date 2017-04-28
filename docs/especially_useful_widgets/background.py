#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

bg = glooey.Background()
bg.set_appearance(
        center=pyglet.resource.texture('center.png'),
        top=pyglet.resource.texture('top.png'),
        bottom=pyglet.resource.texture('bottom.png'),
        left=pyglet.resource.texture('left.png'),
        right=pyglet.resource.texture('right.png'),
        top_left=pyglet.resource.texture('top_left.png'),
        top_right=pyglet.resource.texture('top_right.png'),
        bottom_left=pyglet.resource.texture('bottom_left.png'),
        bottom_right=pyglet.resource.texture('bottom_right.png'),
)
gui.add(bg)

pyglet.app.run()

