#!/usr/bin/env python3

import glooey
import pyglet
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
deck = glooey.Deck('a')
gui.add(deck)

@run_demos.on_space(gui) #
def test_deck():

    green = glooey.Placeholder(50, 50, 'green')
    deck.add_state('a', green)
    yield "Add state 'a'; show a green placeholder"

    orange = glooey.Placeholder(50, 50, 'orange')
    deck.add_state('b', orange)
    yield "Add state 'b'; keep showing state 'a'"

    deck.state = 'b'
    yield "Change to state 'b'; show an orange placeholder"

    purple = glooey.Placeholder(50, 50, 'purple')
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

