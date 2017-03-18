#!/usr/bin/env python3

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

    def __init__(self, image=None):
        super().__init__()
        self._image = image or self.custom_image
        self._sprite = None

    def do_claim(self):
        if self.image is not None:
            return self.image.width, self.image.height
        else:
            return 0, 0

    def do_regroup(self):
        if self._sprite is not None:
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

    def do_undraw(self):
        if self._sprite is not None:
            self._sprite.delete()
            self._sprite = None

    def get_image(self):
        return self._image

    def set_image(self, new_image):
        if self._image is not new_image:
            self._image = new_image
            self.repack()

    def del_image(self):
        self.set_image(None)


@autoprop
class Background(Widget):
    custom_color = None
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

    def __init__(self):
        super().__init__()
        self._artist = drawing.Background(
                color=self.custom_color,
                image=self.custom_image,
                center=self.custom_center,
                top=self.custom_top,
                bottom=self.custom_bottom,
                left=self.custom_left,
                right=self.custom_right,
                top_left=self.custom_top_left,
                top_right=self.custom_top_right,
                bottom_left=self.custom_bottom_left,
                bottom_right=self.custom_bottom_right,
                vtile=self.custom_vtile,
                htile=self.custom_htile,
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
        self._artist.unhide()

    def do_undraw(self):
        self._artist.hide()

    def get_color(self):
        return self._artist.color

    def set_color(self, new_color):
        self._artist.color = new_color

    def get_images(self):
        return self._artist.images

    def set_images(self, *, color=None, image=None, center=None, top=None,
            bottom=None, left=None, right=None, top_left=None, top_right=None,
            bottom_left=None, bottom_right=None, vtile=None, htile=None):

        self._artist.set_images(
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
        self.repack()

    def set_image(self, image):
        self._artist.set_image(image)
        self.repack()

    @property
    def is_empty(self):
        return self._artist.is_empty


@autoprop
class Frame(Widget):
    Bin = Bin
    Decoration = Background
    custom_alignment = 'center'
    custom_bin_layer = 2
    custom_decoration_layer = 1

    def __init__(self):
        super().__init__()

        self._bin = self.Bin()
        self._decoration = self.Decoration()

        self._attach_child(self._bin)
        self._attach_child(self._decoration)

    def add(self, child):
        self._bin.add(child)

    def clear(self):
        self._bin.clear()

    def do_claim(self):
        return claim_stacked_widgets(self._bin, self._decoration)

    def do_regroup_children(self):
        self._bin.regroup(pyglet.graphics.OrderedGroup(
            self.custom_bin_layer, self.group))
        self._decoration.regroup(pyglet.graphics.OrderedGroup(
            self.custom_decoration_layer, self.group))

    def get_bin(self):
        return self._bin

    def get_decoration(self):
        return self._decoration


@autoprop
class Outline(Frame):
    custom_color = 'green'
    custom_decoration_layer = 2
    custom_bin_layer = 1

    class Decoration(Widget):

        def __init__(self):
            super().__init__()
            self.artist = drawing.Outline(hidden=True)

        def do_claim(self):
            return 2, 2

        def do_attach(self):
            self.artist.batch = self.batch

        def do_resize(self):
            self.artist.rect = self.rect

        def do_regroup(self):
            self.artist.group = self.group

        def do_draw(self):
            self.artist.unhide()

        def do_undraw(self):
            self.artist.hide()


    def __init__(self, color=None):
        super().__init__()
        self.color = color or self.custom_color

    def get_color(self):
        return self.decoration.artist.color

    def set_color(self, new_color):
        self.decoration.artist.color = drawing.Color.from_anything(new_color)
        self.decoration.draw()


