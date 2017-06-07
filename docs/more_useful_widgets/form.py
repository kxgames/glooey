#!/usr/bin/env python3

import glooey
import pyglet

pyglet.font.add_file('Lato-Regular.ttf')
pyglet.font.load('Lato Regular')

class WesnothForm(glooey.Form):
    custom_alignment = 'center'

    class Label(glooey.EditableLabel):
        custom_font_name = 'Lato Regular'
        custom_font_size = 10
        custom_color = '#b9ad86'
        custom_alignment = 'top left'
        custom_horz_padding = 5
        custom_top_padding = 5
        custom_width_hint = 200

    class Base(glooey.Background):
        custom_center = pyglet.resource.texture('form_center.png')
        custom_left = pyglet.resource.image('form_left.png')
        custom_right = pyglet.resource.image('form_right.png')

window = pyglet.window.Window()
gui = glooey.Gui(window)

form = WesnothForm()
form.push_handlers(on_unfocus=lambda w: print(f"Form input: '{w.text}'"))
gui.add(form)

pyglet.app.run()

