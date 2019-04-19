#!/usr/bin/env python3

"""
Widget that appear in front of everything else to quickly communicate something 
to the user.
"""

import pyglet
import autoprop

from glooey.text import Label
from glooey.images import Background
from glooey.buttons import Button
from glooey.containers import Grid, HBox, Frame
from glooey.misc import Spacer
from glooey.helpers import *

@autoprop
@register_event_type('on_close')
class Dialog(Frame):

    def open(self, gui):
        self.close()
        gui.add(self)

    def close(self):
        if self.root is not None:
            self.root.remove(self)
            self.dispatch_event('on_close', self)

@autoprop
class ButtonDialog(Dialog):
    Box = Grid
    Content = Label
    custom_autoadd_content = False

    class Buttons(HBox):
        custom_alignment = 'right'

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.__content = self.Content(*args, **kwargs)
        self.__buttons = self.Buttons()

        self.box.add(0, 0, self.__content)
        self.box.add(1, 0, self.__buttons)
        self.box.set_row_height(1, 0)

    def add(self, widget):
        self.box.add(0, 0, widget)
        self.__content = widget

    def clear(self):
        self.remove(0, 0)

    def get_content(self):
        return self.__content

    def get_buttons(self):
        return self.__buttons

    def _replace_button(self, old_button, new_button, on_click):
        old_button.remove_handlers(on_click)
        new_button.push_handlers(on_click=on_click)
        self.__buttons.replace(old_button, new_button)
    

@autoprop
class OkDialog(ButtonDialog):

    class OkButton(Button): #
        class Label(Label):
            custom_text = 'Ok'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ok_button = self.OkButton()
        self._ok_button.push_handlers(on_click=self.on_click_ok)
        self.buttons.pack(self._ok_button)

    def on_click_ok(self, widget):
        self.close()

    def get_ok_button(self):
        return self._ok_button

    def set_ok_button(self, button):
        self._replace_button(self._ok_button, button, self.on_click_ok)
        self._ok_button = button


@autoprop
class YesNoDialog(ButtonDialog):

    class YesButton(Button): #
        class Label(Label):
            custom_text = 'Ok'

    class NoButton(Button): #
        class Label(Label):
            custom_text = 'Cancel'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._yes_button = self.YesButton()
        self._yes_button.push_handlers(on_click=self.on_click_yes)
        self._no_button = self.NoButton()
        self._no_button.push_handlers(on_click=self.on_click_no)
        self._response = False

        self.buttons.pack(self._yes_button)
        self.buttons.pack(self._no_button)

    def open(self, gui):
        self._response = None
        super().open(gui)

    def on_click_yes(self, widget):
        self._response = True
        self.close()

    def on_click_no(self, widget):
        self._response = False
        self.close()

    def get_yes_button(self):
        return self._yes_button

    def set_yes_button(self, button):
        self._replace_button(self._yes_button, button, self.on_click_yes)
        self._yes_button = button

    def get_no_button(self):
        return self._no_button

    def set_no_button(self, button):
        self._replace_button(self._no_button, button, self.on_click_no)
        self._no_button = button

    def get_response(self):
        return self._response


