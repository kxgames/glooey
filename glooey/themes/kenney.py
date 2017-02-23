#!/usr/bin/env python3

theme = glooey.themes.ResourceLoader('kenney')
theme.add_font('font/kenvector_future.ttf')


class LabelButton(glooey.Button):

    class Label(glooey.Label): #
        custom_color = 'white'
        custom_bold = 'True'
        custom_font_name = 'KenVector Future'
        custom_font_size = 12

    custom_label_placement = 'center'

    def on_rollover(self, new_state, old_state):
        def down_placement(child_rect, parent_rect):
            child_rect.center = parent_rect.center
            child_rect.bottom -= 4

        if new_state == 'down':
            self.set_label_placement(down_placement)
        if old_state == 'down':
            self.set_label_placement('center')


class BlueButton(LabelButton):
    custom_base = theme.image('png/blue_button04.png')
    custom_down = theme.image('png/blue_button05.png')

class RedButton(LabelButton):
    custom_base = theme.image('png/blue_button04.png')
    custom_down = theme.image('png/blue_button05.png')


