#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)

edge = pyglet.image.load('frame-edge.png')
corner = pyglet.image.load('frame-corner.png')

frame = glooey.Frame()
frame.set_edge(edge, 'top')
frame.set_corner(corner, 'top left')

widget = glooey.PlaceHolder()

frame.add(widget)
root.add(frame)

pyglet.app.run()


