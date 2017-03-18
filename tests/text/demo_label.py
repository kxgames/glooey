#!/usr/bin/env python3

import pyglet
import glooey
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt. Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae. Sed ut justo massa, varius molestie diam. Sed lacus quam, tempor in dictum sed, posuere et diam.'
gui = glooey.Gui(window, batch=batch)
stack = glooey.Stack()
stack.alignment = 'center'
label = glooey.Label()
outline = glooey.PlaceHolder(color='purple')
stack.add(outline)
stack.add(label)
gui.add(stack)

@demo_helpers.interactive_tests(window, batch) #
def test_label():
    label.set_text('Lorem ipsum', 0)
    yield "Display \"lorem ipsum\"."
    
    label.text = ''
    yield "Clear the label."

    label.set_text(lorem_ipsum, 400)
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

