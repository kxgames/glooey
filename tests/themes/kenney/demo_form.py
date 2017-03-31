#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney
import run_demos

window = pyglet.window.Window()
gui = kenney.Gui(window)
form = kenney.Form('Lorem ipsum...')
form.alignment = 'center'
form.width_hint = 200
gui.add(form)

pyglet.app.run()


