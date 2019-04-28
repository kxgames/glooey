#!/usr/bin/env python3

import glooey
import pyglet

pyglet.font.add_file('Lato-Regular.ttf')
pyglet.font.load('Lato Regular')

# This script is just meant to demonstrate how one widget can be positioned 
# within another.  THIS IS NOT THE BEST WAY TO MAKE A DIALOG BOX.  If you want 
# a dialog box, consider using OkDialog or YesNoDialog.  Only inherit directly 
# from Dialog if neither of those classes meet your needs.

class WesnothDialog(glooey.Dialog):

    class Box(glooey.Bin):
        custom_right_padding = 14
        custom_top_padding = 14
        custom_left_padding = 17
        custom_bottom_padding = 17

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

class WesnothButton(glooey.Button):

    class Foreground(glooey.Label):
        custom_font_name = 'Lato Regular'
        custom_font_size = 10
        custom_color = '#b9ad86'
        custom_alignment = 'center'

    custom_base_image = pyglet.resource.image('base.png')
    custom_over_image = pyglet.resource.image('over.png')
    custom_down_image = pyglet.resource.image('down.png')

window = pyglet.window.Window()
gui = glooey.Gui(window)

dialog = WesnothDialog()
dialog.size_hint = 300, 200

button = WesnothButton('Ok')
button.alignment = 'bottom right'

dialog.add(button)
dialog.open(gui)

button.debug_placement_problems(
        claimed='black', content='orange', assigned='green')

pyglet.app.run()

