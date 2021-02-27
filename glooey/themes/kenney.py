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
assets = ResourceLoader('kenney')
assets.add_font('font/kenvector_future.ttf')
assets.add_font('font/kenvector_future_thin.ttf')

glooey.drawing.colors = {
        'light blue': glooey.Color.from_hex('#35baf3'),
        'blue': glooey.Color.from_hex('#1ea7e1'),
        'dark blue': glooey.Color.from_hex('#166e93'),

        'light red': glooey.Color.from_hex('#fa8132'),
        'red': glooey.Color.from_hex('#e86a17'),
        'dark red': glooey.Color.from_hex('#aa4e11'),

        'light green': glooey.Color.from_hex('#88e060'),
        'green': glooey.Color.from_hex('#73cd4b'),
        'dark green': glooey.Color.from_hex('#47832c'),

        'light yellow': glooey.Color.from_hex('#ffd948'),
        'yellow': glooey.Color.from_hex('#ffcc00'),
        'dark yellow': glooey.Color.from_hex('#a88600'),

        'white': glooey.Color.from_hex('#ffffff'),
        'light grey': glooey.Color.from_hex('#eeeeee'),
        'dark grey': glooey.Color.from_hex('#aaaaaa'),
        'black': glooey.Color.from_hex('#000000'),
}


@autoprop
class BigLabel(glooey.Label):
    custom_color = 'dark grey'
    custom_font_name = 'KenVector Future'
    custom_font_size = 12

@autoprop
class Label(glooey.Label):
    custom_color = 'dark grey'
    custom_font_name = 'KenVector Future Thin'
    custom_font_size = 10

@autoprop
class Form(glooey.Form):

    class Label(glooey.EditableLabel):
        custom_padding = 14
        custom_top_padding = 12
        custom_bottom_padding = 10
        custom_color = 'dark grey'
        custom_selection_color = 'white'
        custom_selection_background_color = 'blue'
        custom_font_name = 'KenVector Future Thin'
        custom_font_size = 10
    
    class Base(glooey.Background):
        custom_center = assets.texture('form/center.png')
        custom_top = assets.texture('form/top.png')
        custom_left = assets.texture('form/left.png')
        custom_right = assets.texture('form/right.png')
        custom_bottom = assets.texture('form/bottom.png')
        custom_top_left = assets.image('form/top_left.png')
        custom_top_right = assets.image('form/top_right.png')
        custom_bottom_left = assets.image('form/bottom_left.png')
        custom_bottom_right = assets.image('form/bottom_right.png')



@autoprop
class Frame(glooey.Frame):
    custom_color = 'grey'

    class Box(glooey.Bin):
        custom_padding = 18

    def __init__(self):
        super().__init__()
        self.color = self.custom_color

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        style = f'frames/{self._color}'
        self.decoration.set_appearance(
                center=assets.texture(f'{style}/center.png'),
                top=assets.texture(f'{style}/top.png'),
                left=assets.texture(f'{style}/left.png'),
                bottom=assets.texture(f'{style}/bottom.png'),
                right=assets.texture(f'{style}/right.png'),
                top_left=assets.image(f'{style}/top_left.png'),
                top_right=assets.image(f'{style}/top_right.png'),
                bottom_left=assets.image(f'{style}/bottom_left.png'),
                bottom_right=assets.image(f'{style}/bottom_right.png'),
        )


@autoprop
class BlueFrame(Frame):
    custom_color = 'blue'

@autoprop
class RedFrame(Frame):
    custom_color = 'red'

@autoprop
class GreenFrame(Frame):
    custom_color = 'green'

@autoprop
class YellowFrame(Frame):
    custom_color = 'yellow'

@autoprop
class GreyFrame(Frame):
    custom_color = 'grey'


@autoprop
class Menu(glooey.Widget):
    custom_color = 'blue'
    custom_text = None
    custom_alignment = 'center'

    class Title(Label):
        custom_alignment = 'center'
        custom_color = 'white'
        custom_top_padding = 12
        custom_bottom_padding = 8

    class Header(glooey.Frame):
        custom_alignment = 'fill horz'

    class Body(Frame):
        custom_alignment = 'fill'


    def __init__(self, title=None):
        super().__init__()

        self._vbox = glooey.VBox()
        self._title = self.Title(title or self.custom_text)
        self._header = self.Header()
        self._body = self.Body()

        self._header.add(self._title)
        self._vbox.add(self._header, 0)
        self._vbox.add(self._body)
        self._attach_child(self._vbox)

        self.color = self.custom_color

    def add(self, widget):
        self._body.add(widget)

    def clear(self):
        self._body.clear()

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color

        header = f'frames/{self._color}'
        body = f'frames/grey'

        self._header.decoration.set_appearance(
                center=assets.texture(f'{header}/center.png'),
                top=assets.texture(f'{header}/top.png'),
                left=assets.texture(f'{header}/left.png'),
                right=assets.texture(f'{header}/right.png'),
                top_left=assets.image(f'{header}/top_left.png'),
                top_right=assets.image(f'{header}/top_right.png'),
        )
        self._body.decoration.set_appearance(
                center=assets.texture(f'{body}/center.png'),
                bottom=assets.texture(f'{body}/bottom.png'),
                left=assets.texture(f'{body}/left.png'),
                right=assets.texture(f'{body}/right.png'),
                bottom_left=assets.image(f'{body}/bottom_left.png'),
                bottom_right=assets.image(f'{body}/bottom_right.png'),
        )


@autoprop
class BlueMenu(Menu):
    custom_color = 'blue'

@autoprop
class RedMenu(Menu):
    custom_color = 'red'

@autoprop
class GreenMenu(Menu):
    custom_color = 'green'

@autoprop
class YellowMenu(Menu):
    custom_color = 'yellow'

    class Title(Menu.Title):
        custom_color = 'dark yellow'



class HRule(glooey.Background):
    custom_center = assets.texture('dividers/horz.png')
    custom_htile = True
    custom_vtile = False
    custom_vert_padding = 8

class VRule(glooey.Background):
    custom_center = assets.texture('dividers/vert.png')
    custom_htile = False
    custom_vtile = True
    custom_horz_padding = 18


@autoprop
class Button(glooey.Button):
    custom_color = 'blue' # 'red', 'green', 'yellow', 'grey'
    custom_gloss = 'high' # 'low', 'matte'
    custom_font_color = 'white'

    class Foreground(Label):
        custom_alignment = 'center'
        custom_font_weight = 'bold'
        custom_horz_padding = 30

    def __init__(self, text=None):
        super().__init__(text)

        self._color = self.custom_color
        self._gloss = self.custom_gloss
        self._update_background()

        self.foreground.color = self.custom_font_color

    def on_rollover(self, widget, new_state, old_state):
        if new_state == 'down':
            self.foreground.top_padding = 2 * 4
        if old_state == 'down':
            self.foreground.top_padding = 0

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        self._update_background()

    def get_gloss(self):
        return self._gloss

    def set_gloss(self, new_gloss):
        self._gloss = new_gloss
        self._update_background()

    def _update_background(self):
        gloss = {
                'high': 'high_gloss',
                'low': 'low_gloss',
                'matte': 'matte',
        }
        style = f'buttons/{self._color}/{gloss[self._gloss]}'
        self.set_background(
                base_left=assets.image(f'{style}/base_left.png'),
                base_center=assets.texture(f'{style}/base_center.png'),
                base_right=assets.image(f'{style}/base_right.png'),
                down_left=assets.image(f'{style}/down_left.png'),
                down_center=assets.texture(f'{style}/down_center.png'),
                down_right=assets.image(f'{style}/down_right.png'),
        )


@autoprop
class BlueButton(Button):
    custom_color = 'blue'

@autoprop
class RedButton(Button):
    custom_color = 'red'

@autoprop
class GreenButton(Button):
    custom_color = 'green'

@autoprop
class YellowButton(Button):
    custom_color = 'yellow'
    custom_font_color = 'dark yellow'

@autoprop
class GreyButton(Button):
    custom_color = 'grey'
    custom_font_color = 'dark grey'


@autoprop
class RoundButton(glooey.Button):
    custom_color = 'red'
    custom_icon = 'cross'

    class Foreground(BigLabel):
        custom_color = 'white'
        custom_alignment = 'center'
        custom_font_size = 16


    def __init__(self):
        super().__init__()
        self.color = self.custom_color
        self.icon = self.custom_icon

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        self.set_background(
                base_image=assets.image(f'buttons/{self._color}/round.png'),
        )

    def get_icon(self):
        return self._icon

    def set_icon(self, new_icon):
        self._icon = new_icon
        icon_color = 'grey' if self._color == 'grey' else 'white'
        self.image = assets.image(f'icons/{icon_color}/{self._icon}.png')


@autoprop
class BlueRoundButton(RoundButton):
    custom_color = 'blue'

@autoprop
class RedRoundButton(RoundButton):
    custom_color = 'red'

@autoprop
class GreenRoundButton(RoundButton):
    custom_color = 'green'

@autoprop
class YellowRoundButton(RoundButton):
    custom_color = 'yellow'
    custom_font_color = 'dark yellow'

@autoprop
class GreyRoundButton(RoundButton):
    custom_color = 'grey'
    custom_font_color = 'dark grey'


@autoprop
class Checkbox(glooey.Checkbox):
    custom_color = 'blue'
    custom_icon = 'checkmark' # 'cross'

    def __init__(self):
        super().__init__()
        self._color = self.custom_color
        self._icon = self.custom_icon
        self._update_style()

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        self._update_style()

    def get_icon(self):
        return self._icon

    def set_icon(self, new_icon):
        self._icon = new_icon
        self._update_style()

    def _update_style(self):
        style = f'buttons/{self._color}/checkbox'
        self.set_images(
                checked_base=assets.image(f'{style}/{self._icon}.png'),
                unchecked_base=assets.image(f'{style}/box.png'),
        )


@autoprop
class BlueCheckbox(Checkbox):
    custom_color = 'blue'

@autoprop
class RedCheckbox(Checkbox):
    custom_color = 'red'

@autoprop
class GreenCheckbox(Checkbox):
    custom_color = 'green'

@autoprop
class YellowCheckbox(Checkbox):
    custom_color = 'yellow'

@autoprop
class GreyCheckbox(Checkbox):
    custom_color = 'grey'


@autoprop
class RadioButton(glooey.RadioButton):
    custom_color = 'blue'

    def __init__(self):
        super().__init__()
        self.color = self.custom_color

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        style = f'buttons/{new_color}/radio'
        self.set_images(
                checked_base=assets.image(f'{style}/tick.png'),
                unchecked_base=assets.image(f'{style}/box.png'),
        )


@autoprop
class BlueRadioButton(RadioButton):
    custom_color = 'blue'

@autoprop
class RedRadioButton(RadioButton):
    custom_color = 'red'

@autoprop
class GreenRadioButton(RadioButton):
    custom_color = 'green'

@autoprop
class YellowRadioButton(RadioButton):
    custom_color = 'yellow'

@autoprop
class GreyRadioButton(RadioButton):
    custom_color = 'grey'


