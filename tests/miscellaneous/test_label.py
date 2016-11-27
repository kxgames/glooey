#!/usr/bin/env python

import pyglet
import glooey

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt. Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae. Sed ut justo massa, varius molestie diam. Sed lacus quam, tempor in dictum sed, posuere et diam. Maecenas tincidunt enim elementum turpis blandit tempus. Nam lectus justo, adipiscing vitae ultricies egestas, porta nec diam. Aenean ac neque tortor. Cras tempus lacus nec leo ultrices suscipit. Etiam sed aliquam tortor. Duis lacus metus, euismod ut viverra sit amet, pulvinar sed urna.'
root = glooey.Gui(window, batch=batch)
label = glooey.Label(lorem_ipsum)
label.font_size = 12
label.enable_line_wrap(300)
root.add(label)

@window.event
def on_key_press(symbol, modifier):

    if symbol == pyglet.window.key.Q:
        label.bold = not label.bold

    if symbol == pyglet.window.key.W:
        label.italic = not label.italic

    if symbol == pyglet.window.key.E:
        label.underline = not label.underline

    if symbol == pyglet.window.key.A:
        label.color = 'yellow'

    if symbol == pyglet.window.key.S:
        label.color = 'green'

    if symbol == pyglet.window.key.D:
        label.bg_color = 'white'

    if symbol == pyglet.window.key.F:
        label.bg_color = 'black'

    if symbol == pyglet.window.key.Z:
        label.alignment = 'left'

    if symbol == pyglet.window.key.X:
        label.alignment = 'center'

    if symbol == pyglet.window.key.C:
        label.alignment = 'right'

    if symbol == pyglet.window.key.J:
        label.line_spacing = 30

    if symbol == pyglet.window.key.K:
        label.line_spacing = 15

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    label.font_size += scroll_y

pyglet.app.run()

