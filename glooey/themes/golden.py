#!/usr/bin/env python3

import glooey
import pyglet
import autoprop

# Import everything from glooey into this namespace.  We'll overwrite the 
# widgets we want to overwrite and everything else will be directly available.
from glooey import *

# Create a resource loader that knows where the Golden assets are stored.
from glooey.themes import ResourceLoader
resource_loader = ResourceLoader('golden')

@autoprop
class Gui(glooey.Gui):
        
    def __init__(self, window, *, batch=None, cursor='gold'):
        super().__init__(window, batch)
        self.set_cursor(cursor)

    def set_cursor(self, cursor):
        try:
            super().set_cursor(
                    resource_loader.image(f'cursor_{cursor}.png'),
                    resource_loader.yaml(f'cursor_hotspots.yml')[cursor],
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"The Golden theme doesn't have a cursor named '{cursor}'")


@autoprop
class RoundButton(glooey.Button):

    def __init__(self, color, icon=None):
        super().__init__()
        self.color = color
        self.icon = icon

    def get_color(self):
        return self._color

    def set_color(self, color):
        try:
            self._color = color
            self.set_backgrounds(
                    base=resource_loader.image(f'icon_{color}_base.png'),
                    over=resource_loader.image(f'icon_{color}_over.png'),
                    down=resource_loader.image(f'icon_{color}_down.png'),
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{color}' button.")

    def get_icon(self):
        return self._icon

    def set_icon(self, name):
        if name is None:
            return self.unset_icon()

        try:
            self._icon = name
            self.set_foreground(
                    resource_loader.image(f'icon_{name}.png'),
            )
        except pyglet.resource.ResourceNotFoundException:
            raise UsageError(f"the Golden theme doesn't have a '{name}' icon.")

    def unset_icon(self):
        self.unset_foreground()


class Frame:
    pass

class Header:
    pass

class Slots:
    pass
