#!/usr/bin/env python3

import pyglet
import glooey
import itertools as it
import run_demos

class MyHBox(glooey.HBox):
    custom_cell_padding = 10

class MyButton(glooey.Button):
    custom_base_color = 'green'
    custom_over_color = 'orange'
    custom_down_color = 'purple'
    custom_size_hint = 20, 20

class MyScrollBox(glooey.ScrollBox):

    class VBar(glooey.VScrollBar):
        Forward = MyButton
        Backward = MyButton
        Grip = MyButton

class MyForm(glooey.Form):

    class Base(glooey.Background):
        custom_outline = 'green'

    class Focused(glooey.Background):
        custom_outline = 'orange'

hbox = MyHBox()
text = MyForm()
scroll = MyScrollBox()
content = glooey.Placeholder(200, 300)

hbox.add(text, 'expand')
hbox.add(scroll, 'expand')
scroll.add(content)

window = pyglet.window.Window(width=450, height=200)
gui = glooey.Gui(window)
gui.add(hbox)

@run_demos.on_space(gui)
def test_40():
    yield "Focus on the form (left), then drag the scroll grip."

pyglet.app.run()
