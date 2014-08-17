#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

cursor = pyglet.image.load('cursor-image.png')
hotspot = 4, 24

root = glooey.PanningGui(window, cursor, hotspot, batch=batch)
viewport = glooey.Viewport()
menu = glooey.PlaceHolder(height=200, color=glooey.drawing.purple)
widgets = [
        glooey.PlaceHolder(width=300, height=900),
        glooey.EventLogger(width=200, height=900, color=glooey.drawing.yellow),
        glooey.PlaceHolder(width=300, height=900),
]

hbox = glooey.HBox(padding=50)
for logger in widgets: hbox.add(logger)

viewport.set_center_of_view(500, 500)
viewport.wrap(hbox)

vbox = glooey.VBox()
vbox.add(viewport, expand=True)
vbox.add(menu)

root.wrap(vbox)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

