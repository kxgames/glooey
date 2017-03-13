#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
gui = golden.Gui(window)
frame = golden.SmallFrame()
hbox = golden.HBox(0)
vrule = golden.VRule()
labels = [ #
        golden.Label('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt.', line_wrap=200),
        golden.Label('Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae.', line_wrap=200),
]

hbox.add(labels[0])
hbox.add(vrule)
hbox.add(labels[1])
frame.add(hbox)
gui.add(frame)

pyglet.app.run()


