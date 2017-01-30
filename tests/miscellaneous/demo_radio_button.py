#!/usr/bin/env python3

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = glooey.Gui(window, batch=batch)
hbox = glooey.HBox(padding=5, placement='center')
theme = glooey.themes.ResourceLoader('wesnoth')

class WesnothRadioButton(glooey.RadioButton):
    default_unchecked_base = theme.image('buttons/checkbox.png')
    default_unchecked_over = theme.image('buttons/checkbox-active.png')
    default_unchecked_down = theme.image('buttons/checkbox-touched.png')
    default_checked_base = theme.image('buttons/checkbox-pressed.png')
    default_checked_over = theme.image('buttons/checkbox-active-pressed.png')
    default_checked_down = theme.image('buttons/checkbox-touched.png')

def on_toggle(widget):
    print(f"{widget}: {widget.is_checked}")

buttons = []
for i in range(3):
    button = WesnothRadioButton(buttons)
    button.push_handlers(on_toggle=on_toggle)
    hbox.add(button)

root.add(hbox, 'center')

pyglet.app.run()

