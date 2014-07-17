#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

cursor = pyglet.image.load('cursor-image.png')
hotspot = 4, 24

root = glooey.GuiWithExclusiveMouse(window, cursor, hotspot, batch=batch)
viewport = glooey.Viewport()
widget = glooey.PlaceHolder(width=1000, height=1000)

root.wrap(viewport)
viewport.wrap(widget)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

