#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

class TestOutline(glooey.Frame):

    class Box(glooey.Bin):
        custom_padding = 2
        custom_width_hint = 200

    class Decoration(glooey.Background):
        custom_outline = 'green'



window = pyglet.window.Window()
gui = glooey.Gui(window)
vbox = glooey.VBox()
frames = [ #
        TestOutline(),
        TestOutline(),
]
labels = [ #
        glooey.EditableLabel(),
        glooey.EditableLabel('Lorem ipsum.'),
]

vbox.alignment = 'center'
vbox.padding = 10

for frame, label in zip(frames, labels):
    label.push_handlers(on_unfocus=lambda w: print(f"{w}: '{w.text}'"))
    frame.add(label)
    vbox.add(frame)

gui.add(vbox)

@run_demos.on_space(gui) #
def test_label():
    yield "Type into the forms."

    for label in labels: 
        label.selection_color = 'white'
        label.selection_background_color = 'orange'

    yield "Orange and white selected text."

    for label in labels: 
        label.selection_color = 'black'
        label.selection_background_color = 'green'

    for label in labels: 
        label.unfocus_on_enter = False

    yield "Allow newlines to be entered."

    for label in labels: 
        label.unfocus_on_enter = True

pyglet.app.run()

