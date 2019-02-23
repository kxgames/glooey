#!/usr/bin/env python3

import glooey
import pyglet

win = pyglet.window.Window(800, 600)

gui = glooey.Gui(win)

box = glooey.Placeholder(50, 50)
box.padding = 100 
box.alignment = "fill right"
gui.add(box)

#p = glooey.Placeholder(50, 50)
#box.add(p)

box.debug_placement_problems()
pyglet.app.run()
