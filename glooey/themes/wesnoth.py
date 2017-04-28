#!/usr/bin/env python3

assets = glooey.themes.ResourceLoader('wesnoth')
assets.add_font('fonts/Lato-Regular.ttf')

class WesnothButton(glooey.Button):

    class Label(glooey.Label): #
        custom_color = '#b9ad86'
        custom_font_name = 'Lato Regular'
        custom_font_size = 10

    custom_base = assets.image('buttons/button_normal/button_H22.png')
    custom_over = assets.image('buttons/button_normal/button_H22-active.png')
    custom_down = assets.image('buttons/button_normal/button_H22-pressed.png')
    custom_label_placement = 'center'

class BraidedFrame:
    pass

class GildedFrame:
    pass
