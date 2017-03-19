#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
stack = glooey.Stack()
stack.alignment = 'center'
label = glooey.Label()
outline = glooey.PlaceHolder(color='purple')
stack.add(outline)
stack.add(label)
gui.add(stack)

@run_demos.on_space(gui) #
def test_label():
    label.set_text('Lorem ipsum', 0)
    yield "Display \"lorem ipsum\"."
    
    label.text = ''
    yield "Clear the label."

    label.set_text(glooey.drawing.lorem_ipsum(10), 400)
    yield "Display wrapped text."

    label.font_name = 'serif'
    yield "Use a serif font."
    del label.font_name

    label.font_size = 8
    yield "Decrease the font size to 8."
    del label.font_size

    label.bold = True
    yield "Make the text bold."
    del label.bold

    label.italic = True
    yield "Make the text italic."
    del label.italic

    label.underline = True
    yield "Underline the text."
    # Explicitly set underline to False (rather than using ``del``) because the 
    # underline machinery handles True and False specially, so I want to make 
    # sure it works with both.
    label.underline = False

    label.color = 'orange'
    yield "Make the text orange."
    label.color = 'green'

    label.background_color = 'orange'
    yield "Make the background orange."
    del label.background_color

    label.text_alignment = 'center'
    yield "Center-align the text."

    label.text_alignment = 'right'
    yield "Right-align the text."
    del label.text_alignment

    label.line_spacing = 30
    yield "Increase the line-spacing to 30px."
    del label.line_spacing

    label.kerning = 2
    yield "Increase the kerning to 2px."
    del label.kerning

pyglet.app.run()

