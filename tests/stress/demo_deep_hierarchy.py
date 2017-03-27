#!/usr/bin/env python3

"""\
Test how deeply widgets can be nested.

The test is simply to make a bin that contains a bin that contains a bin... and 
on and on until finally the last bin just contains a button.  This puts stress 
on the recursion that glooey makes fairly heavy use of.  

The test was meant to be to make sure that the button remains responsive, but 
after running it I realized that glooey hits python's recursion limit after 
only ~200 levels of nesting.  200 levels is a lot, but it's conceivable a real 
GUI could want that many (since so many of the widgets are pretty deeply nested 
themselves).
"""

import pyglet
import glooey

print(__doc__)

import sys
#sys.setrecursionlimit(...)
print(f"Recursion limit: {sys.getrecursionlimit()} frames")


class TestButton(glooey.Button):
    custom_size_hint = 50, 50

    class Base(glooey.Background):
        custom_color = 'green'

    class Over(glooey.Background):
        custom_color = 'orange'

    class Down(glooey.Background):
        custom_color = 'purple'



window = pyglet.window.Window()
gui = glooey.Gui(window)
bins = [glooey.Bin() for i in range(200)]
button = TestButton()

for i in range(1, len(bins)):
    bins[i-1].add(bins[i])

bins[-1].add(button)
gui.add(bins[0])

pyglet.app.run()

