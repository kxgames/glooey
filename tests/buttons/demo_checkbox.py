#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestCheckbox(glooey.Checkbox): #
    custom_checked_base = pyglet.image.load('assets/misc/checked_base.png')
    custom_checked_over = pyglet.image.load('assets/misc/checked_over.png')
    custom_checked_down = pyglet.image.load('assets/misc/checked_down.png')
    custom_checked_off = pyglet.image.load('assets/misc/checked_off.png')

    custom_unchecked_base = pyglet.image.load('assets/misc/unchecked_base.png')
    custom_unchecked_over = pyglet.image.load('assets/misc/unchecked_over.png')
    custom_unchecked_down = pyglet.image.load('assets/misc/unchecked_down.png')
    custom_unchecked_off = pyglet.image.load('assets/misc/unchecked_off.png')

window = pyglet.window.Window()
gui = glooey.Gui(window)
button = TestCheckbox()
gui.add(button)

@button.event #
def on_toggle(widget):
    print(f"{widget} is {'checked' if widget.is_checked else 'unchecked'}!")

@run_demos.on_space(gui) #
def test_checkbox():
    yield "Green button with orange over and purple down states."
    button.disable()
    yield "Grey inactive button (no rollover)."
    button.enable()

    gui.clear()
    hbox = glooey.HBox()
    proxy = glooey.Placeholder(100, 10)

    hbox.pack(button)
    hbox.pack(proxy)

    hbox.alignment = 'center'
    hbox.padding = 10

    gui.add(hbox)
    button.add_proxy(proxy)

    yield "Rollover or click the placeholder to control the button."

    gui.clear()
    hbox.remove(button)
    gui.add(button)

pyglet.app.run()

