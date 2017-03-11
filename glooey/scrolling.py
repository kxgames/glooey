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
    # Don't limit horz/vert motion.  Requiring that the child stay inside the 
    # mover should be good enough.
    custom_initial_position = 'top left'

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
        self._child_position = None
        self._translate_group = None
        self._initial_position = self.custom_initial_position

    @vecrec.accept_anything_as_vector
    def pan(self, step):
        self._require_mover_and_child_rects()
        self._child_position += step
        self._keep_child_in_rect()

    @vecrec.accept_anything_as_vector
    def pan_percent(self, step_percent):
        self.pan(step_percent * (self.rect.size - self.child.rect.size))

    @accept_alignment_or_vector
    def jump(self, new_position):
        """
        Parameters
        ==========
        new_position: str | func | vector | tuple
            The new position for the child widget, which can be specified in 
            several different ways:
            
            First, you can give an alignment string that doesn't change the 
            size of its target.  So 'top left' and 'center' are allowed, but 
            'fill' isn't.  
            
            Second, you can give a function that takes two rectangles and 
            positions the first relative to the second, without changing the 
            size of either one.  
            
            Third, you can give a vector, or any object that can be converted 
            into a vector (e.g. anything that can be unpacked to two items, or 
            has 'x' and 'y' attributes).  This will specify the offset between 
            the bottom-left corner of the mover and the bottom left corner of 
            the child.
            
            Fourth, you can give the 'x' and 'y' coordinates as two separate 
            arguments.  These will be cast to a vector and treated as such.
        """
        self._require_mover_and_child_rects()

        if isinstance(new_position, Vector):
            self._child_position = new_position

        else:
            child_rect = self.child.rect.copy()
            drawing.fixed_size_align(new_position, child_rect, self.rect)
            self._child_position = child_rect.bottom_left - self.rect.bottom_left

        self._keep_child_in_rect()
        

    @vecrec.accept_anything_as_vector
    def jump_percent(self, new_position_percent):
        """
        new_percent should be between -1.0 and 1.0.  Values outside this range 
        are not illegal, but they will be clamped into it.
        """
        self.jump(new_position_percent * (self.rect.size - self.child.rect.size))

    def do_resize_children(self):
        # Make the child whatever size it wants to be.
        self.child.resize(self.child.claimed_rect)

        # If the offset vector hasn't been set yet, set it based on the initial 
        # view requested by the user.  This has to be done after the child is 
        # resized, because self.jump() requires that the child have a rect.
        if self._child_position is None:
            self.jump(self._initial_position)

    def do_regroup_children(self):
        self._translate_group = self.TranslateGroup(self, self.group)
        self.child.regroup(self._translate_group)

    def on_remove_child(self, child):
        self._child_position = None

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

    def get_child_position(self):
        return self._child_position

    def get_initial_position(self):
        return self.initial_position

    @accept_alignment_or_vector
    def set_initial_position(self, new_position):
        self._initial_position = new_position

    @vecrec.accept_anything_as_vector
    def screen_to_child_coords(self, screen_coords):
        mover_origin = self.rect.bottom_left
        mover_coords = screen_coords - mover_origin
        child_origin = self.child.rect.bottom_left
        child_coords = child_origin - self._child_position + mover_coords
        return child_coords

    @vecrec.accept_anything_as_vector
    def child_to_screen_coords(self, child_coords):
        child_origin = self.child.rect.bottom_left
        pane_origin = self.rect.bottom_left
        pane_coords = child_coords - child_origin - self._child_position
        screen_coords = pane_coords + pane_origin
        return screen_coords

    def _keep_child_in_rect(self):
        self._child_position.x = clamp(
                self._child_position.x,
                0, 
                self.rect.width - self.child.rect.width,
        )
        self._child_position.y = clamp(
                self._child_position.y,
                0,
                self.rect.height - self.child.rect.height,
        )

    def _require_mover_and_child_rects(self):
        if self.child is None:
            raise UsageError("can't pan/jump until the mover has a child widget.")

        if self.rect is None:
            raise UsageError("can't pan/jump until the mover has been given a size.")

        if self.child.rect is None:
            raise UsageError("can't pan/jump until the mover's child has been given a size.")



@autoprop
class ScrollPane(Bin):
    custom_initial_view = 'top left'
    custom_horz_scrolling = False
    custom_vert_scrolling = False

    class ScrollGroup(pyglet.graphics.Group):

        def __init__(self, pane, parent=None):
            pyglet.graphics.Group.__init__(self, parent)
            self.pane = pane

        def set_state(self):
            translation = -self.pane.screen_to_child_coords(0, 0)
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(translation.x, translation.y, 0)

        def unset_state(self):
            pyglet.gl.glPopMatrix()


    def __init__(self):
        super().__init__()

        # The offset_vector is the displacement between the bottom-left corner 
        # of this widget and the bottom-left corner of the child widget.
        self._offset_vector = None

        # The initial_view is an alignment string or function that will be used 
        # to set the initial offset.  It must not change the size of the child.
        self._initial_view = self.custom_initial_view

        # The scissor_group manages the clipping mask to make sure the child is 
        # only visible inside the pane.  The panning_group member is used to 
        # translate the child in response to scroll events.
        self._scissor_group = None
        self._scroll_group = None

        # Keep track of the dimensions that are allowed to scroll.
        self._horz_scrolling = self.custom_horz_scrolling
        self._vert_scrolling = self.custom_vert_scrolling

    @vecrec.accept_anything_as_vector
    def jump(self, new_offset):
        """
        Offset specified from bottom left corner.
        """
        if self._horz_scrolling:
            self._offset_vector.x = new_offset.x
        if self._vert_scrolling:
            self._offset_vector.y = new_offset.y
        self._keep_offset_in_bounds()

    @vecrec.accept_anything_as_vector
    def jump_percent(self, new_percent):
        """
        new_percent should be between -1.0 and 1.0.  Values outside this range 
        are not illegal, but they will be clamped into it.
        """
        self.jump(new_percent * (self.child.rect.size - self.rect.size))

    @vecrec.accept_anything_as_vector
    def scroll(self, delta_offset):
        if self._horz_scrolling:
            self._offset_vector.x += delta_offset.x
        if self._vert_scrolling:
            self._offset_vector.y += delta_offset.y
        self._keep_offset_in_bounds()

    @vecrec.accept_anything_as_vector
    def scroll_percent(self, delta_percent):
        self.scroll(delta_percent * (self.child.rect.size - self.rect.size))

    def do_claim(self):
        # The widget being displayed in the scroll pane can claim however much 
        # space it wants in the dimension being scrolled.  The scroll pane 
        # itself doesn't need to claim any space, because it can be as small as 
        # it needs to be.
        min_width = 0 if self._horz_scrolling else self.child.claimed_width
        min_height = 0 if self._vert_scrolling else self.child.claimed_height
        return min_width, min_height

    def do_resize(self):
        # Update the region that will be clipped by OpenGL, unless the widget 
        # hasn't been assigned a group yet.
        if self._scissor_group:
            self._scissor_group.rect = self.rect

    def do_resize_children(self):
        # Make the child whatever size it wants to be.
        self.child.resize(self.child.claimed_rect)

        # If the offset vector hasn't been set yet, set it based on the initial 
        # view requested by the user.
        if self._offset_vector is None:
            self.set_view(self._initial_view)

    def do_regroup_children(self):
        self._scissor_group = drawing.ScissorGroup(self.rect, self.group)
        self._scroll_group = self.ScrollGroup(self, self._scissor_group)
        self.child.regroup(self._scroll_group)

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

    def get_view(self):
        if not self.rect:
            return None
        return Rect.from_bottom_left(
                self._offset_vector, self.rect.width, self.rect.height)

    def set_view(self, new_alignment):
        # In order to set the center of view, the sizes of the scroll pane 
        # widget and its child are needed.  Unfortunately this information is 
        # not available until the scroll pane has been attached to a root 
        # widget and given a child.  To allow this method to be called at any 
        # time, the _initial_view member is used in conjunction with 
        # do_resize_children() to cache and apply the desired center of view.
        if (self.rect is None) or (self.child is None) or (self.child.rect is None):
            self._initial_view = new_alignment
            return

        new_view = Rect.from_size(*self.rect.size)
        alignment_func = drawing.cast_to_alignment(new_alignment)
        alignment_func(new_view, self.child.rect)

        if new_view.size != self.rect.size:
            raise UsageError(f"""\
the alignment function used to set the view in a {self.__class__.__name__} must not change the shape of its first argument.

The given function '{new_alignment}' changed its first argument from {'x'.join(self.rect.size)} to {'x'.join(new_view.size)}.  A common way to get this error is to use one of the 'fill' alignments.  Instead, limit yourself to 'top left', 'bottom right', etc.""")

        self._offset_vector = new_view.bottom_left - self.child.rect.bottom_left
        self._keep_offset_in_bounds()

    def get_horz_scrolling(self):
        return self._horz_scrolling

    def set_horz_scrolling(self, new_setting):
        self._horz_scrolling = new_setting
        self.repack()

    def get_vert_scrolling(self):
        return self._vert_scrolling

    def set_vert_scrolling(self, new_setting):
        self._vert_scrolling = new_setting
        self.repack()

    @vecrec.accept_anything_as_vector
    def screen_to_child_coords(self, screen_coords):
        pane_origin = self.rect.bottom_left
        pane_coords = screen_coords - pane_origin
        child_origin = self.child.rect.bottom_left
        child_coords = child_origin + self._offset_vector + pane_coords
        return child_coords

    @vecrec.accept_anything_as_vector
    def child_to_screen_coords(self, child_coords):
        child_origin = self.child.rect.bottom_left
        pane_origin = self.rect.bottom_left
        pane_coords = child_coords - child_origin - self._offset_vector
        screen_coords = pane_coords + pane_origin
        return screen_coords

    def _keep_offset_in_bounds(self):
        self._offset_vector.x = clamp(
                self._offset_vector.x,
                0, 
                abs(self.child.rect.width - self.rect.width),
        )
        self._offset_vector.y = clamp(
                self._offset_vector.y,
                0,
                abs(self.child.rect.height - self.rect.height),
        )


class ScrollBar(Widget):
    Slider = Button
    Forward = Button
    Backward = Button

    class Slider(Button):

        class ScrollGroup(pyglet.graphics.Group):

            def __init__(self, pane, parent=None):
                pyglet.graphics.Group.__init__(self, parent)
                self.pane = pane

            def set_state(self):
                translation = -self.pane.screen_to_child_coords(0, 0)
                pyglet.gl.glPushMatrix()
                pyglet.gl.glTranslatef(translation.x, translation.y, 0)

            def unset_state(self):
                pyglet.gl.glPopMatrix()

        def __init__(self, bar):
            super().__init__(self)
            self.bar = bar

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


class ScrollBox(Widget):
    pass
