#!/usr/bin/env python3

import pyglet
import glooey
import autoprop
import datetime
from vecrec import Vector, Rect

@autoprop
class Ring(glooey.Widget):
    custom_radius = 150

    def __init__(self, radius=None):
        super().__init__()
        self._children = []
        self._radius = radius or self.custom_radius

    def get_children(self):
        # Return a copy of the list so the caller can't mess up our internal 
        # state by adding or removing things.
        return self._children[:]

    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        self._repack()

    def add(self, widget):
        self.insert(widget, len(self._children))

    def insert(self, widget, index):
        self._attach_child(widget)
        self._children.insert(index, widget)
        self._repack_and_regroup_children()

    def replace(self, old_widget, new_widget):
        i = self._children.index(old_widget)
        with self.hold_updates():
            self.remove(old_widget)
            self.insert(new_widget, i)

    def remove(self, widget):
        self._detach_child(widget)
        self._children.remove(widget)
        self._repack_and_regroup_children()

    def clear(self):
        with self.hold_updates():
            for child in self._children[:]:
                self.remove(child)

    def do_claim(self):
        top = bottom = left = right = 0

        for child, offset in self._yield_offsets():
            top = max(top, offset.y + child.claimed_height / 2)
            bottom = min(bottom, offset.y - child.claimed_height / 2)
            left = min(left, offset.x - child.claimed_width / 2)
            right = max(right, offset.x + child.claimed_width / 2)

        return right - left, top - bottom

    def do_resize_children(self):
        for child, offset in self._yield_offsets():
            rect = child.claimed_rect.copy()
            rect.center = self.rect.center + offset
            child._resize(rect)

    def _yield_offsets(self):
        N = len(self._children)
        for i, child in enumerate(self._children):
            offset = self.radius * Vector.from_degrees(360 * i / N)
            yield child, offset



window = pyglet.window.Window()
gui = glooey.Gui(window)
ring = Ring(radius=150)

for i in range(10):
    green = glooey.Placeholder(50, 50)
    ring.add(green)

for i in range(0, 10, 2):
    orange = glooey.Placeholder(50, 50, 'orange')
    ring.replace(ring.children[i], orange)

gui.add(ring)
pyglet.app.run()

