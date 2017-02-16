#!/usr/bin/env python3

"""\
There are 5 place-holders, each of a different color, but only one should be 
visible at a time.  Make sure there are no errors if all the place-holders are 
deleted.

space:  Replace the current place-holder with the next one.
d:      Remove the current place-holder form the rotation.
"""

import glooey
import pyglet
import demo_helpers

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
root = glooey.Gui(window, batch=batch)
deck = glooey.Deck('a')
root.add(deck)

@demo_helpers.interactive_tests(window, batch) #
def test_deck():

    green = glooey.PlaceHolder(50, 50, 'green')
    deck.add_state('a', green)
    yield "Add state 'a'; show a green placeholder"

    orange = glooey.PlaceHolder(50, 50, 'orange')
    deck.add_state('b', orange)
    yield "Add state 'b'; keep showing state 'a'"

    deck.state = 'b'
    yield "Change to state 'b'; show an orange placeholder"

    purple = glooey.PlaceHolder(50, 50, 'purple')
    deck.add_state('b', purple)
    yield "Replace state 'b'; show a purple placeholder."

    deck.reset_states(a=orange, c=green)
    yield "Reset the deck with states 'a' and 'c'; don't show anything."

    deck.state = 'c'
    yield "Change to state 'c'; show a green placeholder"

    deck.remove_state('c')
    yield "Remove state 'c'; don't show anything."

    deck.state = 'a'
    yield "Change to state 'a'; show an orange placeholder"

    deck.clear()
    yield "Clear the deck; don't show anything."

pyglet.app.run()

