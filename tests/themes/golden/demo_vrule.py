#!/usr/bin/env python3

import pyglet
import glooey.themes.golden as golden

window = pyglet.window.Window()
root = golden.Gui(window)
frame = golden.SmallFrame()
hbox = golden.HBox()
vrule = golden.VRule()
labels = [ #
        golden.Label('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt.', line_wrap=200),
        golden.Label('Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae.', line_wrap=200),
]

hbox.default_size = 0
hbox.add(labels[0])
hbox.add(vrule)
hbox.add(labels[1])
frame.add(hbox)
root.add(frame)

pyglet.app.run()

