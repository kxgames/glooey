#!/usr/bin/env python3

import glooey
import pyglet
import autoprop

# Import everything from glooey into this namespace.  We'll overwrite the 
# widgets we want to overwrite and everything else will be directly available.
from glooey import *

# Create a resource loader that knows where the Golden assets are stored.
from glooey.themes import ResourceLoader
assets = ResourceLoader('golden')
assets.add_font('fonts/m5x7.ttf')

@autoprop
class Gui(glooey.Gui):
    default_cursor = 'gold'
        
    def __init__(self, window, *, batch=None, cursor=None):
        super().__init__(window, batch)
        self.set_cursor(cursor or self.default_cursor)

    def set_cursor(self, cursor):
        try:
            super().set_cursor(
                    assets.image(f'cursors/{cursor}.png'),
                    assets.yaml(f'cursors/hotspots.yml')[cursor],
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"The Golden theme doesn't have a cursor named '{cursor}'")


class Label(glooey.Label):
    default_font_name = 'm5x7'
    default_color = '#deeed6'

@autoprop
class RoundButton(glooey.Button):
    default_color = 'red'
    defult_icon = None

    def __init__(self, color=None, icon=None):
        super().__init__()
        self.color = color or self.default_color
        self.icon = icon or self.default_icon

    def get_color(self):
        return self._color

    def set_color(self, color):
        try:
            self._color = color
            self.set_background(
                    base=assets.image(f'buttons/round/{color}_base.png'),
                    over=assets.image(f'buttons/round/{color}_over.png'),
                    down=assets.image(f'buttons/round/{color}_down.png'),
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{color}' button.")

    def get_icon(self):
        return self._icon

    def set_icon(self, name):
        if name is None:
            return self.del_image()
        try:
            self._icon = name
            self.set_image(
                    assets.image(f'buttons/round/icon_{name}.png'),
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{name}' icon.")

    def del_icon(self):
        self.del_image()


@autoprop
class FancyButton(glooey.Button):
    default_htile = True

    class Label(glooey.Label):
        # "Wellmere Sans" is proprietary, so it cannot be included with glooey.
        default_font_name = 'wellmere_sans_bold'
        default_color = '#140c1c'
        default_alignment = 'center'
        default_horz_padding = 30

    class Base(glooey.Background):
        default_left = assets.image(f'buttons/fancy/left_base.png')
        default_center = assets.texture(f'buttons/fancy/center_base.png')
        default_right = assets.image(f'buttons/fancy/right_base.png')

    class Over(glooey.Background):
        default_left = assets.image(f'buttons/fancy/left_over.png')
        default_center = assets.texture(f'buttons/fancy/center_over.png')
        default_right = assets.image(f'buttons/fancy/right_over.png')

    class Down(glooey.Background):
        default_left = assets.image(f'buttons/fancy/left_down.png')
        default_center = assets.texture(f'buttons/fancy/center_down.png')
        default_right = assets.image(f'buttons/fancy/right_down.png')


class RadioButton(glooey.RadioButton):
    default_checked_base = assets.image('buttons/radio/checked.png')
    default_unchecked_base = assets.image('buttons/radio/unchecked.png')


class Frame:
    pass

class Header:
    pass

class Slots:
    pass
