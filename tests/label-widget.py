#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt. Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae. Sed ut justo massa, varius molestie diam. Sed lacus quam, tempor in dictum sed, posuere et diam. Maecenas tincidunt enim elementum turpis blandit tempus. Nam lectus justo, adipiscing vitae ultricies egestas, porta nec diam. Aenean ac neque tortor. Cras tempus lacus nec leo ultrices suscipit. Etiam sed aliquam tortor. Duis lacus metus, euismod ut viverra sit amet, pulvinar sed urna.'
root = glooey.Gui(window, batch=batch)
label = glooey.Label(lorem_ipsum)
label.set_alignment('center')
label.enable_line_wrap(300)
label.claim()
print(label.min_width, label.min_height)
root.add(label)
pyglet.app.run()

