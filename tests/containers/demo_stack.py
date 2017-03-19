#!/usr/bin/env python3

import pyglet
import glooey
import run_demos

window = pyglet.window.Window()
gui = glooey.Gui(window)
stack = glooey.Stack()
gui.add(stack)

@run_demos.on_space(gui) #
def test_stack():

    def layer(size, color='green'): #
        size = size * (window.height - 20)
        return glooey.EventLogger(size, size, color, align='center')

    stack.add(layer(0.8, 'green'))
    stack.add(layer(0.4, 'orange'))
    assert stack.layers == [1, 0]
    yield "Make a stack with two layers."

    stack.one_child_gets_mouse = True
    yield "Only one child gets each mouse event."
    stack.one_child_gets_mouse = False

    stack.add_front(layer(0.2, 'red'))
    assert stack.layers == [2, 1, 0]
    yield "Add a red layer in front."

    stack.add_back(layer(1.0, 'blue'))
    assert stack.layers == [2, 1, 0, -1]
    yield "Add a blue layer in back."

    stack.insert(layer(0.6, 'yellow'), 0.5)
    yield "Add a yellow layer in the middle."

    stack.remove(stack.children[0])
    yield "Remove the front layer."

    stack.remove(stack.children[0])
    yield "Remove the front layer again."

    stack.clear()
    yield "Clear the stack."

pyglet.app.run()

