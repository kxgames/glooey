#!/usr/bin/env python3

import pyglet
import glooey

pyglet.font.add_file('Lato-Regular.ttf')
pyglet.font.load('Lato Regular')

class WesnothLabel(glooey.Label):
    custom_font_name = 'Lato Regular'
    custom_font_size = 10
    custom_color = '#b9ad86'
    custom_alignment = 'center'

class WesnothButton(glooey.Button):
    Foreground = WesnothLabel
    Background = glooey.Image
    custom_base_image = pyglet.resource.image('base.png')
    custom_over_image = pyglet.resource.image('over.png')
    custom_down_image = pyglet.resource.image('down.png')

class WesnothDialog(glooey.YesNoDialog):

    class Decoration(glooey.Background):
        custom_center = pyglet.resource.texture('center.png')
        custom_top = pyglet.resource.texture('top.png')
        custom_bottom = pyglet.resource.texture('bottom.png')
        custom_left = pyglet.resource.texture('left.png')
        custom_right = pyglet.resource.texture('right.png')
        custom_top_left = pyglet.resource.image('top_left.png')
        custom_top_right = pyglet.resource.image('top_right.png')
        custom_bottom_left = pyglet.resource.image('bottom_left.png')
        custom_bottom_right = pyglet.resource.image('bottom_right.png')

    class Box(glooey.Grid):
        custom_right_padding = 14
        custom_top_padding = 14
        custom_left_padding = 17
        custom_bottom_padding = 17
        custom_cell_padding = 9

    class Buttons(glooey.HBox):
        custom_cell_padding = 3
        custom_alignment = 'right'

    class YesButton(WesnothButton):
        custom_text = 'Ok'

    class NoButton(WesnothButton):
        custom_text = 'Cancel'

window = pyglet.window.Window()
gui = glooey.Gui(window)

dialog = WesnothDialog()
dialog.add(glooey.Placeholder(300, 200))
dialog.open(gui)

pyglet.app.run()




