#!/usr/bin/env python3

import glooey
import pyglet

window = pyglet.window.Window()
gui = glooey.Gui(window)

button = glooey.Button("Click here!")
button.push_handlers(on_click=lambda w: print(f"{w} clicked!"))
gui.add(button)

pyglet.app.run()

