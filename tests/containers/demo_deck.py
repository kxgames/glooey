#!/usr/bin/env python3

"""\
There are 5 place-holders, each of a different color, but only one should be 
visible at a time.  Make sure there are no errors if all the place-holders are 
deleted.

space:  Replace the current place-holder with the next one.
d:      Remove the current place-holder form the rotation.
"""

import pyglet
import demo_helpers
from glooey import *
from glooey.drawing import *

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

states = ['red', 'orange', 'yellow', 'green', 'blue']
next_state = 0

root = Gui(window, batch=batch)
deck = Deck(states[next_state])
root.add(deck)

@window.event
def on_key_press(symbol, modifiers): #
    global next_state
    if symbol == pyglet.window.key.SPACE and states:
        next_state = (next_state + 1) % len(states)
        deck.state = states[next_state]

    if symbol == pyglet.window.key.D and states:
        deck.remove_state(states.pop(next_state))
        if states:
            next_state = next_state % len(states)
            deck.state = states[next_state]

pyglet.app.run()

