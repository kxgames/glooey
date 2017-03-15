#!/usr/bin/env python3

import pyglet
import vecrec
import autoprop

from vecrec import Vector, Rect
from debugtools import p, pp, pv
from .widget import Widget
from .containers import Bin, Grid, HVBox, HBox, VBox
from .miscellaneous import Frame, Button, Image
from .helpers import *
from . import drawing

@autoprop
class Mover(Bin):

    class TranslateGroup(pyglet.graphics.Group):

        def __init__(self, mover, parent=None):
            pyglet.graphics.Group.__init__(self, parent)
            self.mover = mover

        def set_state(self):
            translation = -self.mover.screen_to_child_coords(0, 0)
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(int(translation.x), int(translation.y), 0)

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
        self.jump(self.position + step)

    @vecrec.accept_anything_as_vector
    def pan_percent(self, step_percent):
        self._require_rects()
        self.pan(step_percent * self.unoccupied_size)

    @vecrec.accept_anything_as_vector
    def jump(self, new_position):
        self._require_rects()
        self._child_position = new_position
        self._keep_child_in_rect()
        self.dispatch_event('on_translate', self)

    @vecrec.accept_anything_as_vector
    def jump_percent(self, new_percent):
        """
        new_percent should be between -1.0 and 1.0.  Values outside this range 
        are not illegal, but they will be clamped into it.
        """
        self._require_rects()
        self.jump(new_percent * self.unoccupied_size)

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

    def get_position(self):
        return self._child_position

    def get_position_percent(self):
        percent = Vector.null()
        ux, uy = self.unoccupied_size
        
        if ux != 0: percent.x = self.position.x / ux
        if uy != 0: percent.y = self.position.y / uy

        return percent

    def get_unoccupied_size(self):
        return self.rect.size - self.child.claimed_rect.size

    @vecrec.accept_anything_as_vector
    def pixels_to_percent(self, pixels):
        percent = Vector.null()
        ux, uy = self.unoccupied_size
        
        if ux != 0: percent.x = pixels.x / ux
        if uy != 0: percent.y = pixels.y / uy

        return percent

    @vecrec.accept_anything_as_vector
    def percent_to_pixels(self, percent):
        return percent * self.unoccupied_size

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

    def _require_rects(self):
        if self.child is None:
            raise UsageError("can't pan/jump until the mover has a child widget.")

        if self.rect is None:
            raise UsageError("can't pan/jump until the mover has been given a size.")

        if self.child.rect is None:
            raise UsageError("can't pan/jump until the mover's child has been given a size.")


Mover.register_event_type('on_translate')

@autoprop
class ScrollPane(Widget):
    Mover = Mover
    custom_initial_view = 'top left'
    custom_horz_scrolling = False
    custom_vert_scrolling = False

    def __init__(self):
        super().__init__()

        self._mover = self.Mover()
        self._mover.push_handlers(self.on_translate)
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

    def do_draw(self):
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

    def on_translate(self, mover):
        self.dispatch_event('on_scroll', self)

    def get_child(self):
        return self._mover.child

    def get_position(self):
        self._require_rects()
        mover_to_pane = self.rect.bottom_left - self._mover.rect.bottom_left
        return mover_to_pane - self._mover.position

    def get_position_percent(self):
        return (1,1) - self._mover.position_percent

    def get_view(self):
        """
        Return the currently visible rectangle in child coordinates.
        """
        mover_to_pane = self.rect.bottom_left - self._mover.rect.bottom_left
        mover_to_child = self._mover.position

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


ScrollPane.register_event_type('on_scroll')

@autoprop
class ScrollGripMixin:
    """
    A widget that is capable of controlling a scroll pane.

    This class cannot be used on its own.  You have to create a new class that 
    inherits from this class and a widget class, and this class has to be at 
    the front of the method resolution order (MRO).  For example:

        class MyGrip(ScrollGripMixin, Button):
            pass
    """

    def __init__(self, mover, pane, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mover = mover
        self.pane = pane
        self.pane.push_handlers(self.on_scroll)
        self.reference_point = None

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        self.grab_mouse()
        self.reference_point = Vector(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)

        if self.reference_point is not None:
            drag_pixels = (x,y) - self.reference_point
            drag_percent = self.mover.pixels_to_percent(drag_pixels)
            self.pane.scroll_percent(drag_percent)
        
    def on_mouse_release(self, x, y, button, modifiers):
        super().on_mouse_release(x, y, button, modifiers)
        self.ungrab_mouse()

    def on_scroll(self, pane):
        self.mover.jump_percent(pane.position_percent)


class ButtonScrollGrip(ScrollGripMixin, Button):
    pass

class ImageScrollGrip(ScrollGripMixin, Image):
    pass

@autoprop
class HVScrollBar(Frame):
    HVBox = HVBox
    Grip = ButtonScrollGrip
    Forward = None
    Backward = None

    custom_alignment = 'fill'
    custom_button_speed = 200 # px/sec

    def __init__(self, pane):
        super().__init__()

        self._pane = pane
        self._hvbox = self.HVBox()
        self._button_speed = self.custom_button_speed

        if self.Backward is not None:
            self._backward = self.Backward()
            self._backward.push_handlers(on_mouse_hold=self.on_backward_click)
            self._hvbox.add(self._backward, 0)

        self._mover = Mover()
        self._grip = self.Grip(self._mover, self._pane)
        self._mover.add(self._grip)
        self._hvbox.add(self._mover)

        if self.Forward is not None:
            self._forward = self.Forward()
            self._forward.push_handlers(on_mouse_hold=self.on_forward_click)
            self._hvbox.add(self._forward, 0)

        self.add(self._hvbox)

    def on_forward_click(self, dt):
        self._pane.scroll(dt * self.button_speed * self.orientation)

    def on_backward_click(self, dt):
        self._pane.scroll(dt * self.button_speed * -self.orientation)

    def get_orientation(self):
        if isinstance(self._hvbox, HBox):
            return Vector(1, 0)
        elif isinstance(self._hvbox, VBox):
            return Vector(0, -1)
        else:
            raise NotImplementedError

    def get_button_speed(self):
        return self._button_speed

    def set_button_speed(self, new_speed):
        self._button_speed = new_speed


@autoprop
class HScrollBar(HVScrollBar):
    HVBox = HBox

@autoprop
class VScrollBar(HVScrollBar):
    HVBox = VBox

@autoprop
class ScrollBox(Widget):
    Pane = ScrollPane
    Frame = None
    HBar = None
    VBar = None
    Corner = None
    custom_mouse_sensitivity = 15 # px/click

    def __init__(self):
        super().__init__()

        self._grid = Grid(2, 2)
        self._grid.set_row_height(1, 0)
        self._grid.set_col_width(1, 0)
        self._attach_child(self._grid)

        self._pane = self.Pane()
        self._pane.horz_scrolling = (self.HBar is not None)
        self._pane.vert_scrolling = (self.VBar is not None)

        self._frame = None
        self._hbar = None
        self._vbar = None
        self._corner = None

        if self.Frame:
            self._frame = self.Frame()
            self._frame.alignment = 'fill'
            self._frame.add(self._pane)
            self._grid.add(0, 0, self._frame)
        else:
            self._grid.add(0, 0, self._pane)

        if self._pane.horz_scrolling:
            self._hbar = self.HBar(self._pane)
            self._grid.add(1, 0, self._hbar)

        if self._pane.vert_scrolling:
            self._vbar = self.VBar(self._pane)
            self._grid.add(0, 1, self._vbar)

        if self.Corner is not None:
            self._corner = self.Corner()
            self._grid.add(1, 1, self._corner)

        self._mouse_sensitivity = self.custom_mouse_sensitivity
    
    def add(self, widget):
        self._pane.add(widget)

    def clear(self):
        self._pane.clear()

    def do_claim(self):
        return self._grid.claimed_size

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._pane.scroll(self.mouse_sensitivity * Vector(scroll_x, scroll_y))

    def get_mouse_sensitivity(self):
        return self._mouse_sensitivity

    def set_mouse_sensitivity(self, new_sensitivity):
        self._mouse_sensitivity = new_sensitivity


@autoprop
class Viewport(ScrollPane):
    custom_horz_scrolling = True
    custom_vert_scrolling = True
    custom_sensitivity = 3

    def __init__(self, sensitivity=None):
        super().__init__()
        self._sensitivity = sensitivity or self.custom_sensitivity

    def do_attach(self):
        # If this line raises a pyglet EventException, you're probably trying 
        # to attach this widget to a GUI that doesn't support mouse pan events.  
        # See the Viewport documentation for more information.
        self.root.push_handlers(self.on_mouse_pan)

    def do_detach(self):
        self.window.remove_handler(self.on_mouse_pan)

    def on_mouse_pan(self, direction, dt):
        self.scroll(direction * self.sensitivity * dt)

    def set_center_of_view(self, new_view):
        self.view = lambda v, _: v.set_center(new_view)

    def get_sensitivity(self):
        return self._sensitivity

    def set_sensitivity(self, new_sensitivity):
        self._sensitivity = new_sensitivity

