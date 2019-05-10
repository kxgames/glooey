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

class WesnothButton(glooey.Button):
    Foreground = WesnothLabel

    class Base(glooey.Image):
        custom_image = pyglet.resource.image('base.png')

    class Over(glooey.Image):
        custom_image = pyglet.resource.image('over.png')

    class Down(glooey.Image):
        custom_image = pyglet.resource.image('down.png')

window = pyglet.window.Window()
gui = glooey.Gui(window)

button = WesnothButton('Click me!')
gui.add(button)

pyglet.app.run()


