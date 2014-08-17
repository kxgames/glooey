#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

base_image = pyglet.image.load('button.png')
over_image = pyglet.image.load('button-over.png')
down_image = pyglet.image.load('button-down.png')

#button = glooey.EventLogger(width=197, height=197)
button = glooey.Button()
button.set_base_image(base_image)
button.set_over_image(over_image)
button.set_down_image(down_image)

bin = glooey.Bin(align='center')
bin.add(button)

root = glooey.Gui(window, batch=batch)
root.padding = 100
root.add(bin)

@button.event
def on_click(button):
    print("Button clicked!")


pyglet.app.run()


