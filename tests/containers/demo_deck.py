#!/usr/bin/env python3

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

for state in states:
    deck.add_state(state, PlaceHolder(50, 50, color=colors[state]))

root.add(deck)

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.TAB and states:
        global next_state
        next_state = (next_state + 1) % len(states)
        deck.state = states[next_state]

    if symbol == pyglet.window.key.D and states:
        deck.remove_state(states.pop())

pyglet.app.run()

