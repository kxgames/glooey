#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

class TestCheckbox(glooey.Checkbox): #
    default_checked_base = pyglet.image.load('assets/misc/checked_base.png')
    default_checked_over = pyglet.image.load('assets/misc/checked_over.png')
    default_checked_down = pyglet.image.load('assets/misc/checked_down.png')
    default_checked_off = pyglet.image.load('assets/misc/checked_off.png')

    default_unchecked_base = pyglet.image.load('assets/misc/unchecked_base.png')
    default_unchecked_over = pyglet.image.load('assets/misc/unchecked_over.png')
    default_unchecked_down = pyglet.image.load('assets/misc/unchecked_down.png')
    default_unchecked_off = pyglet.image.load('assets/misc/unchecked_off.png')

root = glooey.Gui(window, batch=batch)
button = TestCheckbox()
root.add(button)

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

