#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

cursor = pyglet.image.load('cursor-image.png')
hotspot = 4, 24

root = glooey.PanningGui(window, cursor, hotspot, batch=batch)
viewport = glooey.Viewport()
content = glooey.Grid(5, 5, padding=50)
menu = glooey.PlaceHolder(height=200, color=glooey.drawing.purple)
vbox = glooey.VBox()

for row, col in content.yield_cells():
    if row == col:
        style = dict(color=glooey.drawing.yellow)
        WidgetClass = glooey.EventLogger
    else:
        style = dict(color=glooey.drawing.green)
        WidgetClass = glooey.PlaceHolder

    content[row, col] = WidgetClass(width=300, height=200, **style)

viewport.add(content)
vbox.add(viewport, expand=True)
vbox.add(menu)
root.add(vbox)

center_of_view = content[2, 2].rect.center
viewport.set_center_of_view(center_of_view)

pyglet.app.run()

