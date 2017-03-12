#!/usr/bin/env python3

import pyglet
import vecrec
import autoprop

from vecrec import Vector, Rect
from .widget import Widget
from .containers import Bin
from .miscellaneous import Button
from .helpers import *
from . import drawing

def accept_alignment_or_vector(method):
    import functools
    @functools.wraps(method) #
    def decorator(self, x, y=None):
        position = x if y is None else (x,y)
        try: position = vecrec.cast_anything_to_vector(position)
        except vecrec.VectorCastError: pass
        return method(self, position)
    return decorator


@autoprop
class Mover(Bin):

    class TranslateGroup(pyglet.graphics.Group):

        def __init__(self, mover, parent=None):
            pyglet.graphics.Group.__init__(self, parent)
            self.mover = mover

        def set_state(self):
            translation = -self.mover.screen_to_child_coords(0, 0)
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(translation.x, translation.y, 0)

        def unset_state(self):
            pyglet.gl.glPopMatrix()


    def __init__(self):
        super().__init__()
        # child_position is the displacement between the bottom-left corners of 
        # the mover and it child widget.
        self._child_position = Vector.null()
        self._translate_group = None

    @vecrec.accept_anything_as_vector
    def pan(self, step):
        self.translation += step

    @vecrec.accept_anything_as_vector
    def pan_percent(self, step_percent):
        self._require_mover_and_child_rects()
        self.pan(step_percent * (self.rect.size - self.child.claimed_rect.size))

    @vecrec.accept_anything_as_vector
    def jump(self, new_position):
        self.translation = new_position

    @vecrec.accept_anything_as_vector
    def jump_percent(self, new_percent):
        """
        new_percent should be between -1.0 and 1.0.  Values outside this range 
        are not illegal, but they will be clamped into it.
        """
        self._require_mover_and_child_rects()
        self.translation = new_percent * (
                self.rect.size - self.child.claimed_rect.size)

    def do_resize_children(self):
        # Make the child whatever size it wants to be.
        self.child.resize(self.child.claimed_rect)
        self._keep_child_in_rect()

    def do_regroup_children(self):
        self._translate_group = self.TranslateGroup(self, self.group)
        self.child.regroup(self._translate_group)

    def on_remove_child(self, child):
        self._child_position = Vector.null()

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_motion(x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_enter(x, y)

    def on_mouse_leave(self, x, y):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_leave(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_drag_enter(x, y)

    def on_mouse_drag_leave(self, x, y):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_drag_leave(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.screen_to_child_coords(x, y)
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

    def get_translation(self):
        return self._child_position

    def set_translation(self, x, y=None):
        new_position = vecrec.cast_anything_to_vector(x if y is None else (x,y))
        self._require_mover_and_child_rects()
        self._child_position = new_position
        self._keep_child_in_rect()

    @vecrec.accept_anything_as_vector
    def screen_to_child_coords(self, screen_coords):
        mover_origin = self.rect.bottom_left
        mover_coords = screen_coords - mover_origin
        child_origin = self.child.claimed_rect.bottom_left
        child_coords = child_origin - self._child_position + mover_coords
        return child_coords

    @vecrec.accept_anything_as_vector
    def child_to_screen_coords(self, child_coords):
        child_origin = self.child.claimed_rect.bottom_left
        pane_origin = self.rect.bottom_left
        pane_coords = child_coords - child_origin - self._child_position
        screen_coords = pane_coords + pane_origin
        return screen_coords

    def _keep_child_in_rect(self):
        self._child_position.x = clamp(
                self._child_position.x,
                0, 
                self.rect.width - self.child.claimed_rect.width,
        )
        self._child_position.y = clamp(
                self._child_position.y,
                0,
                self.rect.height - self.child.claimed_rect.height,
        )

    def _require_mover_and_child_rects(self):
        if self.child is None:
            raise UsageError("can't pan/jump until the mover has a child widget.")

        if self.rect is None:
            raise UsageError("can't pan/jump until the mover has been given a size.")

        if self.child.rect is None:
            raise UsageError("can't pan/jump until the mover's child has been given a size.")


@autoprop
class ScrollPane(Widget):
    Mover = Mover
    custom_initial_view = 'top left'
    custom_horz_scrolling = False
    custom_vert_scrolling = False

    def __init__(self):
        super().__init__()

        self._mover = self.Mover()
        self._attach_child(self._mover)

        self._scissor_group = None
        self._apply_initial_view = False
        self._initial_view = self.custom_initial_view
        self._horz_scrolling = self.custom_horz_scrolling
        self._vert_scrolling = self.custom_vert_scrolling

    def add(self, child):
        self._mover.add(child)

        if self.is_attached_to_gui:
            self.view = self.initial_view
        else:
            self._apply_initial_view = True

    def clear(self):
        self._mover.clear(child)

    @vecrec.accept_anything_as_vector
    def scroll(self, step):
        self._require_rects()
        self._mover.pan(-step)

    @vecrec.accept_anything_as_vector
    def scroll_percent(self, step_percent):
        self._require_rects()
        self._mover.pan_percent(-step_percent)

    @vecrec.accept_anything_as_vector
    def jump(self, new_position):
        """
        Parameters
        ==========
        new_position: vector-like
            The vector between the bottom left corner of the content and the 
            bottom left corner of the pane.  For example, (0,0) would make the 
            bottom left corner of the content visible.
        """
        self._require_rects()
        mover_to_pane = self.rect.bottom_left - self._mover.rect.bottom_left
        self._mover.jump(mover_to_pane - new_position)

    @vecrec.accept_anything_as_vector
    def jump_percent(self, new_percent):
        self._require_rects()
        self._mover.jump_percent((1,1) - new_percent)

    def do_attach(self):
        if self._apply_initial_view and self.child is not None:
            self._apply_initial_view = False
            self.view = self.initial_view

    def do_claim(self):
        # The widget being displayed in the scroll pane can claim however much 
        # space it wants in the dimension being scrolled.  The scroll pane 
        # itself doesn't need to claim any space in that dimension, because it 
        # can be as small as it needs to be.
        min_width = 0 if self._horz_scrolling else self._mover.claimed_width
        min_height = 0 if self._vert_scrolling else self._mover.claimed_height
        return min_width, min_height

    def do_resize(self):
        # Update the region that will be clipped by OpenGL, unless the widget 
        # hasn't been assigned a group yet.
        if self._scissor_group:
            self._scissor_group.rect = self.rect

    def do_resize_children(self):
        if not self.child:
            return

        mover_rect = self._mover.claimed_rect
        mover_rect.bottom_left = self.rect.bottom_left

        if self._horz_scrolling:
            extra_width = max(mover_rect.width - self.rect.width, 0)
            mover_rect.width += extra_width
            mover_rect.left = self.rect.left - extra_width

        if self._vert_scrolling:
            extra_height = max(mover_rect.height - self.rect.height, 0)
            mover_rect.height += extra_height
            mover_rect.bottom = self.rect.bottom - extra_height

        self._mover.resize(mover_rect)

    def do_regroup_children(self):
        self._scissor_group = drawing.ScissorGroup(self.rect, self.group)
        self._mover.regroup(self._scissor_group)

    def get_child(self):
        return self._mover.child

    def get_view(self):
        """
        Return the currently visible rectangle in child coordinates.
        """
        mover_to_pane = self.rect.bottom_left - self._mover.rect.bottom_left
        mover_to_child = self._mover.translation

        view_rect = self.rect.copy()
        view_rect.bottom_left = mover_to_pane - mover_to_child

        return view_rect

    def set_view(self, new_alignment):
        self._require_rects()

        view_rect = self.rect.copy()
        child_rect = self.child.claimed_rect
        drawing.fixed_size_align(new_alignment, view_rect, child_rect)

        child_to_view = view_rect.bottom_left - child_rect.bottom_left
        self.jump(child_to_view)

    def get_initial_view(self):
        return self._initial_view

    def set_initial_view(self, new_view):
        self._initial_view = new_view

    def get_horz_scrolling(self):
        return self._horz_scrolling

    def set_horz_scrolling(self, new_bool):
        self._horz_scrolling = new_bool
        self.repack()

    def get_vert_scrolling(self):
        return self._vert_scrolling

    def set_vert_scrolling(self, new_bool):
        self._vert_scrolling = new_bool
        self.repack()

    def _require_rects(self):
        if self.child is None:
            raise UsageError("can't scroll until the scroll pane has a child widget.")

        if self.rect is None:
            raise UsageError("can't scroll until the scroll pane has been given a size.")

        if self.child.rect is None:
            raise UsageError("can't scroll until the scroll pane's child has been given a size.")



class ScrollBar(Widget):
    Mover = Mover
    Forward = Button
    Backward = Button

    class Slider(Button):

        def __init__(self, mover):
            self.mover = mover

        def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
            self.mover.pan(dx, dy)


    def __init__(self):
        self._mover = self.Mover()
        self._slider = self.Slider(self._mover)



class ScrollBox(Widget):
    pass
