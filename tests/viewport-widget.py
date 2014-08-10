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
for logger in widgets:
    hbox.add(logger)
viewport.wrap(hbox)

#vbox = glooey.VBox()
#vbox.add(viewport)
#vbox.add(menu)
#
#root.wrap(vbox)
root.wrap(viewport)
print(viewport.min_width, viewport.min_height)
print(hbox.min_width, hbox.min_height)
for widget in widgets:
    print(widget.min_width, widget.min_height)

@window.event
def on_draw():
    window.clear()
    batch.draw()


pyglet.app.run()

