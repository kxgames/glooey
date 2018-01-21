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
    custom_label_padding = 6

    def __init__(self, text):
        super().__init__()

        self.checkbox = WesnothCheckbox()
        self.label = WesnothLabel(text)

        self._attach_child(self.checkbox)
        self._attach_child(self.label)

    def do_claim(self):
        width = sum((
                self.checkbox.claimed_width,
                self.custom_label_padding,
                self.label.claimed_width,
        ))
        height = max(
                self.checkbox.claimed_height,
                self.label.claimed_height,
        )
        return width, height

    def do_resize_children(self):
        checkbox_rect = self.checkbox.claimed_rect
        checkbox_rect.left = self.rect.left
        checkbox_rect.center_y = self.rect.center_y

        label_rect = self.label.claimed_rect
        label_rect.left = checkbox_rect.right + self.custom_label_padding
        label_rect.center_y = self.rect.center_y

        self.checkbox._resize(checkbox_rect)
        self.label._resize(label_rect)


window = pyglet.window.Window()
gui = glooey.Gui(window)
checkbox = WesnothLabeledCheckbox('Toggle something')
gui.add(checkbox)

checkbox.checkbox.push_handlers(on_toggle=lambda w:
        print(f"{w} {'checked' if w.is_checked else 'unchecked'}"))

pyglet.app.run()

