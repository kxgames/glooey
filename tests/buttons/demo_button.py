#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestLabel(glooey.Label): #
    custom_text = 'Custom attribute text'
    custom_color = '#deeed6'
    custom_font_size = 14
    custom_bold = True
    custom_padding = 20


class TestButton(glooey.Button): #
    Foreground = TestLabel

    class Base(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/green.png')

    class Over(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/orange.png')

    class Down(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/purple.png')

    class Off(glooey.Background): #
        custom_center = pyglet.image.load('assets/64x64/grey.png')

class TestButtonNoForeground(TestButton): #
    Foreground = None

class TestButtonCustomAttrIntrospection(glooey.Button): #
    Foreground = TestLabel
    custom_base_center = pyglet.image.load('assets/64x64/green.png')
    custom_over_center = pyglet.image.load('assets/64x64/orange.png')
    custom_down_center = pyglet.image.load('assets/64x64/purple.png')
    custom_off_center  = pyglet.image.load('assets/64x64/grey.png')

class TestButtonSuperclassIntrospection(TestButtonCustomAttrIntrospection):
    pass

window = pyglet.window.Window()
gui = glooey.Gui(window)

def on_click(widget): #
    print(f"{widget} clicked!")

def on_double_click(widget): #
    print(f"{widget} double clicked!")

@run_demos.on_space(gui) #
def test_button():
    button = TestButton()
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "Green button with orange over and purple down states."

    button.disable()
    yield "Grey inactive button (no rollover)."
    button.enable()

    button.set_background(
            base_top    = pyglet.image.load('assets/64x4/green.png'),
            base_bottom = pyglet.image.load('assets/64x4/green.png'),
            base_htile  = True,

            over_top    = pyglet.image.load('assets/64x4/orange.png'),
            over_bottom = pyglet.image.load('assets/64x4/orange.png'),
            over_htile  = True,

            down_top    = pyglet.image.load('assets/64x4/purple.png'),
            down_bottom = pyglet.image.load('assets/64x4/purple.png'),
            down_htile  = True,

            off_top     = pyglet.image.load('assets/64x4/grey.png'),
            off_bottom  = pyglet.image.load('assets/64x4/grey.png'),
            off_htile   = True,
    )
    yield "Replace the background with top and bottom rules."

    button = TestButton('Constructor text')
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "Different button text."

    button = TestButtonNoForeground()
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "No button text."

    button = TestButtonCustomAttrIntrospection("Custom attribute introspection")
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "Custom attribute introspection (same appearance as before)"

    button = TestButtonSuperclassIntrospection("Superclass introspection")
    button.push_handlers(on_click, on_double_click)
    gui.clear(); gui.add(button)
    yield "Superclass introspection (same appearance as before)"


pyglet.app.run()

