#!/usr/bin/env python3

import pyglet
import glooey

class MyForm(glooey.Form):
    custom_alignment = 'center'

    class Label(glooey.EditableLabel): #
        custom_padding = 2
        custom_width_hint = 200

    class Base(glooey.Background): #
        custom_outline = 'green'

    class Focused(glooey.Background): #
        custom_outline = 'orange'

window = pyglet.window.Window(resizable=True)
gui = glooey.Gui(window)
form = MyForm()
gui.add(form)

print("""\
Reproducing the bug
===================
Focus on the form, then resize the window.  Note that the cursor moves outside 
the form.  Clicking on the form or providing input triggers an AttributeError: 
'NoneType' object has no attribute ...
""")
pyglet.app.run()

