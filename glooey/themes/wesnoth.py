#!/usr/bin/env python3

assets = glooey.themes.ResourceLoader('wesnoth')
assets.add_font('fonts/Lato-Regular.ttf')

class WesnothButton(glooey.Button):

    class Label(glooey.Label): #
        default_color = '#b9ad86'
        default_font_name = 'Lato Regular'
        default_font_size = 10

    default_base = assets.image('buttons/button_normal/button_H22.png')
    default_over = assets.image('buttons/button_normal/button_H22-active.png')
    default_down = assets.image('buttons/button_normal/button_H22-pressed.png')
    default_label_placement = 'center'
