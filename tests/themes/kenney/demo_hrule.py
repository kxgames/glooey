#!/usr/bin/env python3

import pyglet
import glooey.themes.kenney as kenney

window = pyglet.window.Window()
gui = kenney.Gui(window)
frame = kenney.Frame()
vbox = kenney.VBox(0)
hrule = kenney.HRule()
labels = [ #
        kenney.Label('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt.', line_wrap=200),
        kenney.Label('Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae.', line_wrap=200),
]

vbox.add(labels[0])
vbox.add(hrule)
vbox.add(labels[1])
frame.add(vbox)
gui.add(frame)

pyglet.app.run()


