#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
vbox = glooey.VBox()
vbox.alignment = 'center'
vbox.padding = 10
gui.add(vbox)

@run_demos.on_space(gui) #
def test_label():

    class TwoStateForm(glooey.Form): #

        class Label(glooey.EditableLabel):
            custom_padding = 2
            custom_width_hint = 200

        class Base(glooey.Background):
            custom_outline = 'green'

        class Focused(glooey.Background):
            custom_outline = 'orange'

    vbox.clear()
    vbox.add(TwoStateForm())
    vbox.add(TwoStateForm('Lorem ipsum.'))

    yield "Two forms that react to being focused."

    class OneStateForm(glooey.Form): #

        class Label(glooey.EditableLabel):
            custom_padding = 2
            custom_width_hint = 200

        class Base(glooey.Background):
            custom_outline = 'green'

    vbox.clear()
    vbox.add(OneStateForm())
    vbox.add(OneStateForm('Lorem ipsum.'))

    yield "Two forms that don't react to being focused."

pyglet.app.run()

