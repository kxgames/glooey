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
    custom_cursor = 'gold'
        
    def __init__(self, window, *, batch=None, cursor=None):
        super().__init__(window, batch)
        self.set_cursor(cursor or self.custom_cursor)

    def set_cursor(self, cursor):
        try:
            super().set_cursor(
                    assets.image(f'cursors/{cursor}.png'),
                    assets.yaml(f'cursors/hotspots.yml')[cursor],
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"The Golden theme doesn't have a cursor named '{cursor}'")


class Label(glooey.Label):
    custom_font_name = 'm5x7'
    custom_color = '#deeed6'

@autoprop
class RoundButton(glooey.Button):
    custom_color = 'red'
    custom_icon = None

    def __init__(self, color=None, icon=None):
        super().__init__()
        self.color = color or self.custom_color
        self.icon = icon or self.custom_icon

    def get_color(self):
        return self._color

    def set_color(self, color):
        try:
            self._color = color
            self.set_background(
                    base_image=assets.image(f'buttons/round/{color}_base.png'),
                    over_image=assets.image(f'buttons/round/{color}_over.png'),
                    down_image=assets.image(f'buttons/round/{color}_down.png'),
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

    class Label(Label):
        custom_horz_padding = 12
        custom_bottom_padding = 3
        custom_alignment = 'center'

    class Base(glooey.Background):
        custom_left=assets.image(f'buttons/basic/base_left.png')
        custom_center=assets.texture('buttons/basic/base_center.png')
        custom_right=assets.image(f'buttons/basic/base_right.png')

    class Down(glooey.Background):
        custom_left=assets.image(f'buttons/basic/down_left.png')
        custom_center=assets.texture('buttons/basic/down_center.png')
        custom_right=assets.image(f'buttons/basic/down_right.png')


@autoprop
class FancyButton(glooey.Button):

    class Label(glooey.Label):
        # "Wellmere Sans" is proprietary, so it cannot be included with glooey.
        custom_font_name = 'wellmere_sans_bold'
        custom_color = '#140c1c'
        custom_alignment = 'center'
        custom_horz_padding = 30

    class Base(glooey.Background):
        custom_left = assets.image(f'buttons/fancy/left_base.png')
        custom_center = assets.texture(f'buttons/fancy/center_base.png')
        custom_right = assets.image(f'buttons/fancy/right_base.png')

    class Over(glooey.Background):
        custom_left = assets.image(f'buttons/fancy/left_over.png')
        custom_center = assets.texture(f'buttons/fancy/center_over.png')
        custom_right = assets.image(f'buttons/fancy/right_over.png')

    class Down(glooey.Background):
        custom_left = assets.image(f'buttons/fancy/left_down.png')
        custom_center = assets.texture(f'buttons/fancy/center_down.png')
        custom_right = assets.image(f'buttons/fancy/right_down.png')


class RadioButton(glooey.RadioButton):
    custom_checked_base = assets.image('buttons/radio/checked.png')
    custom_unchecked_base = assets.image('buttons/radio/unchecked.png')

class BigFrame(glooey.Frame):

    class Decoration(glooey.Background):
        custom_left = assets.image('frames/big/left.png')
        custom_center = assets.texture('frames/big/center.png')
        custom_right = assets.image('frames/big/right.png')

    class Bin(glooey.Bin):
        custom_vert_padding = 16
        custom_horz_padding = 24


class SmallFrame(glooey.Frame):

    class Decoration(glooey.Background):
        custom_center = assets.texture('frames/small/center.png')
        custom_top = assets.texture('frames/small/top.png')
        custom_bottom = assets.texture('frames/small/bottom.png')
        custom_left = assets.texture('frames/small/left.png')
        custom_right = assets.texture('frames/small/right.png')
        custom_top_left = assets.image('frames/small/top_left.png')
        custom_top_right = assets.image('frames/small/top_right.png')
        custom_bottom_left = assets.image('frames/small/bottom_left.png')
        custom_bottom_right = assets.image('frames/small/bottom_right.png')

    class Bin(glooey.Bin):
        custom_padding = 10


class SubFrame(glooey.Frame):

    class Decoration(glooey.Background):
        custom_top = assets.texture('frames/sub/top.png')
        custom_bottom = assets.texture('frames/sub/bottom.png')
        custom_left = assets.texture('frames/sub/left.png')
        custom_right = assets.texture('frames/sub/right.png')
        custom_top_left = assets.image('frames/sub/top_left.png')
        custom_top_right = assets.image('frames/sub/top_right.png')
        custom_bottom_left = assets.image('frames/sub/bottom_left.png')
        custom_bottom_right = assets.image('frames/sub/bottom_right.png')

    class Bin(glooey.Bin):
        custom_padding = 6


class HRule(glooey.Background):
    custom_center = assets.texture('dividers/hrule/center.png')
    custom_left = assets.texture('dividers/hrule/left.png')
    custom_right = assets.texture('dividers/hrule/right.png')
    custom_vert_padding = 3

class VRule(glooey.Background):
    custom_center = assets.texture('dividers/vrule/center.png')
    custom_top = assets.texture('dividers/vrule/top.png')
    custom_bottom = assets.texture('dividers/vrule/bottom.png')
    custom_horz_padding = 3

@autoprop
class BasicFillBar(glooey.FillBar):

    class Base(glooey.Background):
        custom_left = assets.image('fill_bars/basic/base_left.png')
        custom_center = assets.texture('fill_bars/basic/base_center.png')
        custom_right = assets.image('fill_bars/basic/base_right.png')
        custom_htile = True

    class Fill(glooey.Background):
        custom_alignment = 'fill horz'
        custom_horz_padding = 5

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
        custom_left = assets.image('fill_bars/fancy/base_left.png')
        custom_center = assets.texture('fill_bars/fancy/base_center.png')
        custom_right = assets.image('fill_bars/fancy/base_right.png')
        custom_htile = True

    class Fill(glooey.Background):
        custom_alignment = 'fill horz'
        custom_horz_padding = 9

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


