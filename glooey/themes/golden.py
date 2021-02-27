#!/usr/bin/env python3

import glooey
import pyglet
import autoprop

# Import everything from glooey into this namespace.  We'll overwrite the 
# widgets we want to overwrite and everything else will be directly available.
from glooey import *

# Create a resource loader that knows where the assets for this theme are 
# stored.
from glooey.themes import ResourceLoader
assets = ResourceLoader('golden')
assets.add_font('fonts/m5x7.ttf')

@autoprop
class Gui(glooey.Gui):
    custom_cursor = 'gold'
        
    def __init__(self, window, *, batch=None, cursor=None):
        super().__init__(window, batch=batch)
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

class Form(glooey.Form):

    class Label(glooey.EditableLabel):
        custom_font_name = 'm5x7'
        custom_color = '#deeed6'
        custom_selection_color = '#595652'
        custom_padding = 2
        custom_left_padding = 4

    class Base(glooey.Background):
        custom_top = assets.texture('frames/mini/top_left.png')
        custom_left = assets.texture('frames/mini/top_left.png')
        custom_top_left = assets.image('frames/mini/top_left.png')
        custom_bottom = assets.texture('frames/mini/bottom_right.png')
        custom_right = assets.texture('frames/mini/bottom_right.png')
        custom_bottom_right = assets.image('frames/mini/bottom_right.png')


@autoprop
class RoundButton(glooey.Button):
    class Foreground(glooey.Image):
        pass

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
            del self.foreground.image
            return

        try:
            self._icon = name
            self.foreground.image = assets.image(f'buttons/round/icon_{name}.png')
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{name}' icon.")

    def del_icon(self):
        self.del_foreground()


@autoprop
class BasicButton(glooey.Button):

    class Foreground(Label):
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

    class Foreground(Label):
        custom_color = '#140c1c'
        custom_alignment = 'center'
        custom_horz_padding = 30
        custom_font_size = 12

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

    class Box(glooey.Bin):
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

    class Box(glooey.Bin):
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

    class Box(glooey.Bin):
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
            self.fill.set_appearance(
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
            self.fill.set_appearance(
                    left=assets.image(f'fill_bars/fancy/{color}_left.png'),
                    center=assets.texture(f'fill_bars/fancy/{color}_center.png'),
                    right=assets.image(f'fill_bars/fancy/{color}_right.png'),
                    htile=True,
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{color}' fill bar.")


@autoprop
class ScrollBox(glooey.ScrollBox):

    class VBar(glooey.VScrollBar):

        class Decoration(glooey.Background):
            custom_top = assets.image('scroll_bars/bar_top.png')
            custom_center = assets.texture('scroll_bars/bar_center.png')
            custom_bottom = assets.image('scroll_bars/bar_bottom.png')

        class Forward(RoundButton):
            custom_color = 'green'
            custom_icon = 'down'
            custom_top_padding = 6
            custom_bottom_padding = 5
            custom_left_padding = 1
            custom_right_padding = 5

        class Backward(RoundButton):
            custom_color = 'green'
            custom_icon = 'up'
            custom_top_padding = 5
            custom_bottom_padding = 7
            custom_left_padding = 1
            custom_right_padding = 5

        class Grip(glooey.Image):
            custom_image = assets.image('scroll_bars/grip.png')
            custom_left_padding = 2
            custom_right_padding = 6

    class Frame(SmallFrame):

        class Box(SmallFrame.Box):
            custom_top_padding = 6
            custom_bottom_padding = 5


@autoprop
class PopUp(glooey.Dialog):

    class Decoration(glooey.Background):
        custom_left = assets.image('frames/big/left.png')
        custom_center = assets.texture('frames/big/center.png')
        custom_right_padding = 69

    class Box(glooey.Grid):
        custom_default_col_width = 0


    def __init__(self, text=None, line_wrap=None):
        super().__init__()

        self._bin = glooey.Bin()
        self._bin.vert_padding = 16
        self._bin.left_padding = 24

        self._button = glooey.Button()
        self._button.set_background(
                base_image=assets.image('frames/big/right_button_base.png'),
                over_image=assets.image('frames/big/right_button_over.png'),
                down_image=assets.image('frames/big/right_button_down.png'),
                off_image=assets.image('frames/big/right_button_off.png'),
        )
        self._button.push_handlers(on_click=lambda w: self.close())

        self.box.add(0, 0, self._bin)
        self.box.add(0, 1, self._button)

        if text is not None:
            self.set_text(text, line_wrap)

    def add(self, widget):
        self._bin.add(widget)

    def clear(self):
        self._bin.clear()

    def get_button(self):
        return self._button

    def set_text(self, text, line_wrap=None):
        self.add(Label(text, line_wrap))


