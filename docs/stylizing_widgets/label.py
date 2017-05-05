#!/usr/bin/env python3

import glooey
import pyglet

pyglet.font.add_file('Lato-Regular.ttf')
pyglet.font.load('Lato Regular')

class WesnothLabel(glooey.Label):
    custom_font_name = 'Lato Regular'
    custom_font_size = 10
    custom_color = '#b9ad86'
    custom_alignment = 'center'

window = pyglet.window.Window()
gui = glooey.Gui(window)

label = WesnothLabel('Hello world!')
gui.add(label)

pyglet.app.run()


