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
    Label = WesnothLabel
    Checkbox = WesnothCheckbox
    custom_alignment = 'center'

    class HBox(glooey.HBox):
        custom_padding = 6

    def __init__(self, text):
        super().__init__()

        hbox = self.HBox()
        self.checkbox = self.Checkbox()
        self.label = self.Label(text)

        hbox.pack(self.checkbox)
        hbox.add(self.label)

        # Configure `checkbox` to respond to clicks anywhere in `hbox`.
        self.checkbox.add_proxy(hbox, exclusive=True)

        # Make the `on_toggle` events appear to come from this widget.
        self.relay_events_from(self.checkbox, 'on_toggle')

        self._attach_child(hbox)

    def toggle(self):
        self.checkbox.toggle()

    def check(self):
        self.checkbox.check()

    def uncheck(self):
        self.checkbox.uncheck()

    @property
    def is_checked(self):
        return self.checkbox.is_checked

WesnothLabeledCheckbox.register_event_type('on_toggle')

window = pyglet.window.Window()
gui = glooey.Gui(window)
checkbox = WesnothLabeledCheckbox('Toggle something')
gui.add(checkbox)

checkbox.push_handlers(on_toggle=lambda w:
        print(f"{w} {'checked' if w.is_checked else 'unchecked'}"))

pyglet.app.run()

