#!/usr/bin/env python3

import pyglet
import glooey

pyglet.font.add_file('Lato-Regular.ttf')
pyglet.font.load('Lato Regular')

class WesnothScrollBox(glooey.ScrollBox):
    custom_alignment = 'center'
    custom_height_hint = 200

    class Frame(glooey.Frame):

        class Decoration(glooey.Background):
            custom_center = pyglet.resource.texture('center.png')

        class Box(glooey.Bin):
            custom_horz_padding = 2

    class VBar(glooey.VScrollBar):
        custom_scale_grip = True

        class Decoration(glooey.Background):
            custom_top = pyglet.resource.image('bar_top.png')
            custom_center = pyglet.resource.texture('bar_vert.png')
            custom_bottom = pyglet.resource.image('bar_bottom.png')
            custom_vert_padding = 25

        class Forward(glooey.Button):
            custom_base_image = pyglet.resource.image('forward_base.png')
            custom_over_image = pyglet.resource.image('forward_over.png')
            custom_down_image = pyglet.resource.image('forward_down.png')

        class Backward(glooey.Button):
            custom_base_image = pyglet.resource.image('backward_base.png')
            custom_over_image = pyglet.resource.image('backward_over.png')
            custom_down_image = pyglet.resource.image('backward_down.png')

        class Grip(glooey.Button):
            custom_height_hint = 20
            custom_alignment = 'fill'

            custom_base_top = pyglet.resource.image('grip_top_base.png')
            custom_base_center = pyglet.resource.texture('grip_vert_base.png')
            custom_base_bottom = pyglet.resource.image('grip_bottom_base.png')

            custom_over_top = pyglet.resource.image('grip_top_over.png')
            custom_over_center = pyglet.resource.texture('grip_vert_over.png')
            custom_over_bottom = pyglet.resource.image('grip_bottom_over.png')

            custom_down_top = pyglet.resource.image('grip_top_down.png')
            custom_down_center = pyglet.resource.texture('grip_vert_down.png')
            custom_down_bottom = pyglet.resource.image('grip_bottom_down.png')

class WesnothLoremIpsum(glooey.LoremIpsum):
    custom_font_name = 'Lato Regular'
    custom_font_size = 10
    custom_color = '#b9ad86'
    custom_alignment = 'fill horz'

window = pyglet.window.Window()
gui = glooey.Gui(window)

scroll = WesnothScrollBox()
scroll.add(WesnothLoremIpsum())
gui.add(scroll)

pyglet.app.run()

