#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestCheckbox(glooey.Checkbox): #
    custom_checked_base = pyglet.image.load('assets/misc/checked_base.png')
    custom_checked_over = pyglet.image.load('assets/misc/checked_over.png')
    custom_checked_down = pyglet.image.load('assets/misc/checked_down.png')
    custom_checked_off = pyglet.image.load('assets/misc/checked_off.png')

    custom_unchecked_base = pyglet.image.load('assets/misc/unchecked_base.png')
    custom_unchecked_over = pyglet.image.load('assets/misc/unchecked_over.png')
    custom_unchecked_down = pyglet.image.load('assets/misc/unchecked_down.png')
    custom_unchecked_off = pyglet.image.load('assets/misc/unchecked_off.png')

gui = glooey.Gui(window, batch=batch)
button = TestCheckbox()
gui.add(button)

@button.event #
def on_toggle(widget):
    print(f"{widget} is {'checked' if widget.is_checked else 'unchecked'}!")

@demo_helpers.interactive_tests(window, batch) #
def test_checkbox():
    yield "Green button with orange over and purple down states."
    button.deactivate()
    yield "Grey inactive button (no rollover)."
    button.reactivate()

pyglet.app.run()

