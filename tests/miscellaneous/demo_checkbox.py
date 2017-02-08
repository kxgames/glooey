#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
theme = glooey.themes.ResourceLoader('wesnoth')

class WesnothCheckbox(glooey.Checkbox):
    default_unchecked_base = theme.image('buttons/checkbox.png')
    default_unchecked_over = theme.image('buttons/checkbox-active.png')
    default_unchecked_down = theme.image('buttons/checkbox-touched.png')
    default_checked_base = theme.image('buttons/checkbox-pressed.png')
    default_checked_over = theme.image('buttons/checkbox-active-pressed.png')
    default_checked_down = theme.image('buttons/checkbox-touched.png')
    default_alignment = 'center'

root = glooey.Gui(window, batch=batch)
button = WesnothCheckbox()
root.add(button)

@button.event
def on_toggle(widget):
    print(f"{widget} is {'checked' if widget.is_checked else 'unchecked'}!")

pyglet.app.run()

