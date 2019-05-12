#!/usr/bin/env python3

"""
Widgets that can display images
"""

import pyglet
import autoprop

from vecrec import Vector, Rect
from glooey import drawing, containers
from glooey.widget import Widget
from glooey.containers import Bin, claim_stacked_widgets
from glooey.helpers import *

@autoprop
class Image(Widget):
    custom_image = None
    custom_alignment = 'center'

    def __init__(self, image=None, responsive=False):
        if responsive:
            self.custom_alignment = 'fill'
        super().__init__()
        self._image = image or self.custom_image
        self._responsive = responsive
        self._sprite = None

    def do_claim(self):
        if self.image is not None and not self._responsive:
            return self.image.width, self.image.height
        else:
            return 0, 0

    def do_regroup(self):
        if self._sprite is not None:
            self._sprite.batch = self.batch
            self._sprite.group = self.group

    def do_draw(self):
        if self.image is None:
            self.do_undraw()
            return

        if self._sprite is None:
            self._sprite = pyglet.sprite.Sprite(
                    self.image, batch=self.batch, group=self.group)
        else:
            self._sprite.image = self.image

        self._sprite.x = self.rect.left
        self._sprite.y = self.rect.bottom

        if self._responsive:
            scale_x = self.rect.width / self.image.width
            scale_y = self.rect.height / self.image.height
            scale = min(scale_x, scale_y)
            self._sprite.scale = scale

            self._sprite.x += (self.rect.width - self._sprite.width) / 2
            self._sprite.y += (self.rect.height - self._sprite.height) / 2

    def do_undraw(self):
        if self._sprite is not None:
            self._sprite.delete()
            self._sprite = None

    def get_image(self):
        return self._image

    def set_image(self, new_image):
        if self._image is not new_image:
            self._image = new_image
            self._repack()

    def del_image(self):
        self.set_image(None)

    def get_appearance(self):
        return {'image': self._image}

    def set_appearance(self, *, image=None):
        self.set_image(image)

    @property
    def is_empty(self):
        return self._image is None


@autoprop
class Background(Widget):
    custom_color = None
    custom_outline = None
    custom_image = None
    custom_center = None
    custom_top = None
    custom_bottom = None
    custom_left = None
    custom_right = None
    custom_top_left = None
    custom_top_right = None
    custom_bottom_left = None
    custom_bottom_right = None
    custom_vtile = 'auto'
    custom_htile = 'auto'

    def __init__(self, **kwargs):
        super().__init__()
        self._artist = drawing.Background(
                color=kwargs.get('color', self.custom_color),
                outline=kwargs.get('outline', self.custom_outline),
                image=kwargs.get('image', self.custom_image),
                center=kwargs.get('center', self.custom_center),
                top=kwargs.get('top', self.custom_top),
                bottom=kwargs.get('bottom', self.custom_bottom),
                left=kwargs.get('left', self.custom_left),
                right=kwargs.get('right', self.custom_right),
                top_left=kwargs.get('top_left', self.custom_top_left),
                top_right=kwargs.get('top_right', self.custom_top_right),
                bottom_left=kwargs.get('bottom_left', self.custom_bottom_left),
                bottom_right=kwargs.get('bottom_right', self.custom_bottom_right),
                vtile=kwargs.get('vtile', self.custom_vtile),
                htile=kwargs.get('htile', self.custom_htile),
                hidden=True,
        )

    def do_attach(self):
        self._artist.batch = self.batch

    def do_claim(self):
        return self._artist.min_size

    def do_resize(self):
        self._artist.rect = self.rect

    def do_regroup(self):
        self._artist.group = self.group

    def do_draw(self):
        self._artist.show()

    def do_undraw(self):
        self._artist.hide()

    def get_color(self):
        return self._artist.color

    def set_color(self, new_color):
        self._artist.color = new_color

    def get_outline(self):
        return self._artist.outline

    def set_outline(self, new_outline):
        self._artist.outline = new_outline

    def set_image(self, image):
        self._artist.set_image(image)
        self._repack()

    def get_appearance(self):
        return self._artist.appearance

    def set_appearance(self, *, color=None, image=None, center=None, top=None,
            bottom=None, left=None, right=None, top_left=None, top_right=None,
            bottom_left=None, bottom_right=None, vtile='auto', htile='auto'):

        self._artist.set_appearance(
                color=color,
                image=image,
                center=center,
                top=top,
                bottom=bottom,
                left=left,
                right=right,
                top_left=top_left,
                top_right=top_right,
                bottom_left=bottom_left,
                bottom_right=bottom_right,
                vtile=vtile,
                htile=htile,
        )
        self._repack()

    @property
    def is_empty(self):
        return self._artist.is_empty


