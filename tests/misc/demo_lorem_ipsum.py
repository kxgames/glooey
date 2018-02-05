#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)

# Hmmm, label claims more vertical space than it needs because it calculates 
# its claim from its wrapping width, but then flows to fill the whole width 
# available to it.  With big pieces of text, this causes problems...

@run_demos.on_space(gui) #
def test_lorem_ipsum():
    lorem = glooey.LoremIpsum(num_paragraphs=1, line_wrap=640)
    gui.clear(); gui.add(lorem)
    yield "Display 1 paragraph of \"lorem ipsum\"."
    
    lorem = glooey.LoremIpsum(num_paragraphs=2, line_wrap=640)
    gui.clear(); gui.add(lorem)
    yield "Display 2 paragraphs of \"lorem ipsum\"."

    lorem = glooey.LoremIpsum(num_sentences=1, line_wrap=640)
    gui.clear(); gui.add(lorem)
    yield "Display 1 sentence of \"lorem ipsum\"."

    lorem = glooey.LoremIpsum(num_sentences=10, line_wrap=640)
    gui.clear(); gui.add(lorem)
    yield "Display 10 sentences of \"lorem ipsum\"."

pyglet.app.run()

