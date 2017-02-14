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
    default_icon = None

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
class BasicButton(glooey.Button):
    default_htile = True

    class Label(Label):
        default_horz_padding = 12
        default_bottom_padding = 3
        default_alignment = 'center'

    class Base(glooey.Background):
        default_left=assets.image(f'buttons/basic/base_left.png')
        default_center=assets.texture('buttons/basic/base_center.png')
        default_right=assets.image(f'buttons/basic/base_right.png')

    class Down(glooey.Background):
        default_left=assets.image(f'buttons/basic/down_left.png')
        default_center=assets.texture('buttons/basic/down_center.png')
        default_right=assets.image(f'buttons/basic/down_right.png')


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

class BigFrame(glooey.Frame):

    class Background(glooey.Background):
        default_left = assets.image('frames/big/left.png')
        default_center = assets.texture('frames/big/center.png')
        default_right = assets.image('frames/big/right.png')
        default_htile = True

    class Bin(glooey.Bin):
        default_vert_padding = 16
        default_horz_padding = 24


class SmallFrame(glooey.Frame):

    class Background(glooey.Background):
        default_center = assets.texture('frames/small/center.png')
        default_top = assets.texture('frames/small/top.png')
        default_bottom = assets.texture('frames/small/bottom.png')
        default_left = assets.texture('frames/small/left.png')
        default_right = assets.texture('frames/small/right.png')
        default_top_left = assets.image('frames/small/top_left.png')
        default_top_right = assets.image('frames/small/top_right.png')
        default_bottom_left = assets.image('frames/small/bottom_left.png')
        default_bottom_right = assets.image('frames/small/bottom_right.png')
        default_htile = True
        default_vtile = True

    class Bin(glooey.Bin):
        default_padding = 6


class SubFrame:
    pass

@autoprop
class BasicFillBar(glooey.FillBar):

    class Base(glooey.Background):
        default_left = assets.image('fill_bars/basic/base_left.png')
        default_center = assets.texture('fill_bars/basic/base_center.png')
        default_right = assets.image('fill_bars/basic/base_right.png')
        default_htile = True

    class Fill(glooey.Background):
        default_alignment = 'fill horz'
        default_horz_padding = 5

    def __init__(self, fraction_full=0, color='red'):
        super().__init__(fraction_full)
        self.color = color

    def get_color(self):
        return self._color

    def set_color(self, color):
        try:
            self._color = color
            self.fill.set_images(
                    left=assets.image(f'fill_bars/basic/{color}_left.png'),
                    center=assets.texture(f'fill_bars/basic/{color}_center.png'),
                    right=assets.image(f'fill_bars/basic/{color}_right.png'),
                    htile=True,
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{color}' fill bar.")


@autoprop
class FancyFillBar(glooey.FillBar):

    class Base(glooey.Background):
        default_left = assets.image('fill_bars/fancy/base_left.png')
        default_center = assets.texture('fill_bars/fancy/base_center.png')
        default_right = assets.image('fill_bars/fancy/base_right.png')
        default_htile = True

    class Fill(glooey.Background):
        default_alignment = 'fill horz'
        default_horz_padding = 9

    def __init__(self, fraction_full=0, color='red'):
        super().__init__(fraction_full)
        self.color = color

    def get_color(self):
        return self._color

    def set_color(self, color):
        try:
            self._color = color
            self.fill.set_images(
                    left=assets.image(f'fill_bars/fancy/{color}_left.png'),
                    center=assets.texture(f'fill_bars/fancy/{color}_center.png'),
                    right=assets.image(f'fill_bars/fancy/{color}_right.png'),
                    htile=True,
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{color}' fill bar.")


