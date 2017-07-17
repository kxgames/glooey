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

class WesnothCheckbox(glooey.Checkbox):
    custom_checked_base = pyglet.resource.image('checked_base.png')
    custom_checked_over = pyglet.resource.image('checked_over.png')
    custom_checked_down = pyglet.resource.image('unchecked_down.png')
    custom_unchecked_base = pyglet.resource.image('unchecked_base.png')
    custom_unchecked_over = pyglet.resource.image('unchecked_over.png')
    custom_unchecked_down = pyglet.resource.image('unchecked_down.png')

class WesnothLabeledCheckbox(glooey.Widget):
   custom_alignment = 'center'

   def __init__(self, text):
       super().__init__()

       hbox = glooey.HBox()
       self.checkbox = WesnothCheckbox()
       self.label = WesnothLabel(text)

       hbox.pack(self.checkbox)
       hbox.add(self.label)
       hbox.padding = 6

       self._attach_child(hbox)

window = pyglet.window.Window()
gui = glooey.Gui(window)
checkbox = WesnothLabeledCheckbox('Toggle something')
gui.add(checkbox)

checkbox.checkbox.push_handlers(on_toggle=lambda w:
        print(f"{w} {'checked' if w.is_checked else 'unchecked'}"))

pyglet.app.run()

