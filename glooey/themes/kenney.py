#!/usr/bin/env python3

theme = glooey.themes.ResourceLoader('kenney')
theme.add_font('font/kenvector_future.ttf')


class LabelButton(glooey.Button):

    class Label(glooey.Label): #
        default_color = 'white'
        default_bold = 'True'
        default_font_name = 'KenVector Future'
        default_font_size = 12

    default_label_placement = 'center'

    def on_rollover(self, new_state, old_state):
        def down_placement(child_rect, parent_rect):
            child_rect.center = parent_rect.center
            child_rect.bottom -= 4

        if new_state == 'down':
            self.set_label_placement(down_placement)
        if old_state == 'down':
            self.set_label_placement('center')


class BlueButton(LabelButton):
    default_base = theme.image('png/blue_button04.png')
    default_down = theme.image('png/blue_button05.png')

class RedButton(LabelButton):
    default_base = theme.image('png/blue_button04.png')
    default_down = theme.image('png/blue_button05.png')


