#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney

window = pyglet.window.Window()
gui = kenney.Gui(window)
vbox = kenney.VBox()
vbox.alignment = 'center'
vbox.cell_alignment = 'center'
vbox.padding = 16
vbox.add(kenney.BigLabel('Lorem ipsum'))
vbox.add(kenney.Label('dolor sit amet'))
gui.add(vbox)

pyglet.app.run()


