#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestRadioButton(glooey.RadioButton): #
    custom_checked_base = pyglet.image.load('assets/misc/checked_base.png')
    custom_checked_over = pyglet.image.load('assets/misc/checked_over.png')
    custom_checked_down = pyglet.image.load('assets/misc/checked_down.png')
    custom_checked_off = pyglet.image.load('assets/misc/checked_off.png')

    custom_unchecked_base = pyglet.image.load('assets/misc/unchecked_base.png')
    custom_unchecked_over = pyglet.image.load('assets/misc/unchecked_over.png')
    custom_unchecked_down = pyglet.image.load('assets/misc/unchecked_down.png')
    custom_unchecked_off = pyglet.image.load('assets/misc/unchecked_off.png')

def on_toggle(widget): #
    print(f"{widget}: {widget.is_checked}")

window = pyglet.window.Window()
gui = glooey.Gui(window)
hbox = glooey.HBox()
hbox.alignment = 'center'
hbox.cell_alignment = 'center'
hbox.cell_padding = 8

buttons = []
for i in range(3):
    button = TestRadioButton(buttons)
    button.push_handlers(on_toggle=on_toggle)
    hbox.add(button)

gui.add(hbox)

@run_demos.on_space(gui) #
def test_radio_buttons():
    for button in buttons:
        button.enable()
    yield "Three green radio buttons with orange over and purple down states."

    for button in buttons:
        button.disable()
    yield "Grey inactive buttons (no rollover)."

pyglet.app.run()

