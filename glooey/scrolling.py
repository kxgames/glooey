#!/usr/bin/env python3

"""\
Widgets that allow the user to scroll through content that would otherwise be 
too big to fit on the screen.
"""

import math
import pyglet
import vecrec
import autoprop

from vecrec import Vector, Rect
from glooey import drawing
from glooey.widget import Widget
from glooey.containers import Bin, Frame, Grid, HVBox, HBox, VBox
from glooey.buttons import Button
from glooey.images import Image
from glooey.misc import Spacer
from glooey.helpers import *

@autoprop
@register_event_type('on_translate')
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

        # ``child_position`` is the vector between the bottom left corner of 
        # the child's physical position (i.e. it position in it's own 
        # coordinates) and it's apparent position (i.e. the position it seems 
        # to be in after the translation is performed).
        self._child_position = Vector.null()
        self._translate_group = None
        self._expand_horz = True
        self._expand_vert = True

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
        self._child_position = new_position - self.child.padded_rect.bottom_left
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
        # Consult the ``expand_horz`` and ``expand_vert`` member variables to 
        # decide how much space to give the child.  If expansion is enabled, 
        # the child can occupy the whole mover depending on its alignment.  The 
        # advantage of this is that the child can control its initial position 
        # using alignment.  The downside is that widgets with the default 
        # "fill" alignment can't move, which is a gotcha.  If expansion is 
        # disabled, the child is made as small as possible.
        if self.expand_horz:
            child_width = self.rect.width
        else:
            child_width = self.child.claimed_width

        if self.expand_vert:
            child_height = self.rect.height
        else:
            child_height = self.child.claimed_height

        # Put the bottom left corner of the child's rectangle at the origin.  
        # This simplifies the offset calculations, relative to having the 
        # child's rectangle where the parent's is.
        child_rect = Rect.from_size(child_width, child_height)
        self.child._resize(child_rect)
        self._keep_child_in_rect()

    def do_regroup_children(self):
        self._translate_group = self.TranslateGroup(self, self.group)
        self.child._regroup(self._translate_group)

    def on_detach_child(self, parent, child):
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
        return self.child.padded_rect.bottom_left + self._child_position

    def get_position_percent(self):
        percent = Vector.null()
        ux, uy = self.unoccupied_size
        
        if ux != 0: percent.x = self.position.x / ux
        if uy != 0: percent.y = self.position.y / uy

        return percent

    def get_unoccupied_size(self):
        return self.rect.size - self.child.padded_rect.size

    def get_expand_horz(self):
        return self._expand_horz

    def set_expand_horz(self, new_bool):
        self._expand_horz = new_bool
        self._repack()

    def get_expand_vert(self):
        return self._expand_vert

    def set_expand_vert(self, new_bool):
        self._expand_vert = new_bool
        self._repack()

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
        child_coords = mover_coords - self._child_position
        return child_coords

    @vecrec.accept_anything_as_vector
    def child_to_screen_coords(self, child_coords):
        mover_origin = self.padded_rect.bottom_left
        mover_coords = child_coords + self._child_position
        screen_coords = pane_coords + pane_origin
        return screen_coords

    def _keep_child_in_rect(self):
        """
        Update the child position vector to make sure the child can't translate 
        outside the mover.
        """
        self._child_position.x = clamp(
                self._child_position.x,
                -self.child.padded_rect.left,
                self.rect.width - self.child.padded_rect.right,
        )
        self._child_position.y = clamp(
                self._child_position.y,
                -self.child.padded_rect.bottom,
                self.rect.height - self.child.padded_rect.top,
        )

    def _require_rects(self):
        if self.child is None:
            raise UsageError("can't pan/jump until the mover has a child widget.")

        if self.rect is None:
            raise UsageError("can't pan/jump until the mover has been given a size.")

        if self.child.rect is None:
            raise UsageError("can't pan/jump until the mover's child has been given a size.")

@autoprop
@register_event_type('on_scroll')
@register_event_type('on_resize_children')
class ScrollPane(Widget):
    """
    Provide basic support for scrolling.

    ScrollPane implements scrolling using a Mover and a scissor box.  This 
    approach is a little counter-intuitive at first, but it builds really well 
    on the tools and features that already exist.  First, the pane creates a 
    mover that's much bigger than the region that will be visible.  The size of 
    the mover is carefully calculated so that when it's child is all the way at 
    the bottom, it's top is flush with the top of the visible region, and vice 
    versa for the bottom.  The scissor box is then used to clip everything 
    outside the visible region.

    This widget isn't really meant to be used directly.  Instead, it's meant to 
    be a building block for widgets that need scrolling, like ScrollBox and 
    Viewport.
    """
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
        self.horz_scrolling = self.custom_horz_scrolling
        self.vert_scrolling = self.custom_vert_scrolling

    def add(self, child):
        self._mover.add(child)

        if self.is_attached_to_gui:
            self.view = self.initial_view
        else:
            self._apply_initial_view = True

    def clear(self):
        self._mover.clear()

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
        min_width = 0 if self.horz_scrolling else self._mover.claimed_width
        min_height = 0 if self.vert_scrolling else self._mover.claimed_height
        return min_width, min_height

    def do_resize(self):
        # Update the region that will be clipped by OpenGL, unless the widget 
        # hasn't been assigned a group yet.
        if self._scissor_group:
            self._scissor_group.rect = self.rect

    def do_resize_children(self):
        if not self.child:
            return

        mover_rect = self.rect.copy()

        if self.horz_scrolling:
            pane_width = self.rect.width
            content_width = self._mover.claimed_width 
            mover_rect.width = max(2 * content_width - pane_width, pane_width)

        if self.vert_scrolling:
            pane_height = self.rect.height
            content_height = self._mover.claimed_height 
            mover_rect.height = max(2 * content_height - pane_height, pane_height)

        mover_rect.center = self.rect.center

        self._mover._resize(mover_rect)

    def do_regroup_children(self):
        self._scissor_group = drawing.ScissorGroup(self.rect, self.group)
        self._mover._regroup(self._scissor_group)

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
        # This is a bit of a hack.  The mover already has two boolean flags 
        # that indicate whether or not its child should be given the full 
        # amount of space available to the mover.  We can reuse these as 
        # scrolling flags, because we want to give the child the full space in 
        # the dimensions that don't scroll (so that they fill in all the space 
        # allocated to the scroll pane) and not in those that do (so widgets 
        # with alignment='fill' can still be scrolled).
        return not self._mover.expand_horz

    def set_horz_scrolling(self, new_bool):
        # This is a bit of a hack.  See get_horz_scrolling() for more info.
        self._mover.expand_horz = not new_bool
        self._repack()

    def get_vert_scrolling(self):
        # This is a bit of a hack.  See get_horz_scrolling() for more info.
        return not self._mover.expand_vert

    def set_vert_scrolling(self, new_bool):
        # This is a bit of a hack.  See get_horz_scrolling() for more info.
        self._mover.expand_vert = not new_bool
        self._repack()

    def _require_rects(self):
        if self.child is None:
            raise UsageError("can't scroll until the scroll pane has a child widget.")

        if self.rect is None:
            raise UsageError("can't scroll until the scroll pane has been given a size.")

        if self.child.rect is None:
            raise UsageError("can't scroll until the scroll pane's child has been given a size.")

@autoprop
class HVScrollBar(Frame):
    HVBox = HVBox
    Grip = None
    Forward = None
    Backward = None

    class GripMover(Mover):

        def __init__(self, bar, grip):
            super().__init__()
            self.bar = bar
            self.pane = bar._pane
            self.grip = grip
            self.reference_point = None

            self.pane.push_handlers(
                    on_repack=self.on_pane_repack,
                    on_scroll=self.on_pane_scroll,
            )
            self.grip.push_handlers(
                    on_mouse_press=self.on_grip_press,
                    on_mouse_drag=self.on_grip_drag,
            )
            self.grip.grab_mouse_on_click = True
            self.add(grip)

        def do_resize_children(self):
            grip_width, grip_height = self.grip.claimed_size

            if self.bar.scale_grip:
                scaled_width, scaled_height = self.bar._get_scaled_grip_size()
                grip_width = clamp(scaled_width, grip_width, self.width)
                grip_height = clamp(scaled_height, grip_height, self.height)

            # Copied from `Mover.do_resize_children()`; refer there for 
            # details.  Maybe should be more DRY...
            child_rect = Rect.from_size(grip_width, grip_height)
            self.child._resize(child_rect)
            self._keep_child_in_rect()

        def on_grip_press(self, x, y, button, modifiers):
            self.reference_point = Vector(x, y)

        def on_grip_drag(self, x, y, dx, dy, buttons, modifiers):
            if self.reference_point is not None:
                drag_pixels = (x,y) - self.reference_point
                drag_percent = self.pixels_to_percent(drag_pixels)
                self.pane.scroll_percent(drag_percent)

        def on_pane_repack(self):
            if self.bar.scale_grip:
                self._repack()

        def on_pane_scroll(self, pane):
            self.jump_percent(pane.position_percent)


    custom_button_speed = 200
    """\
    How fast to scroll (in px/sec) while the forward and backward buttons are 
    being pressed.
    """

    custom_scale_grip = False
    """\
    If true, scale the grip such that its size relative to the scroll bar is 
    the same as the size of the visible region relative to the total scrollable 
    region.  
    
    Note that this option only affects the space made available to the grip;
    like any other widget, the space it actually occupies depends on its 
    alignment, padding, and size hint parameters.  Pay particular attention to 
    alignment.  `Button` and `Image`, the two most common grip widgets, have 
    ``'center'`` alignments by default.  This means they will not expand to 
    fill the space available to them unless their alignment is changed to 
    ``'fill'`` or similar.
    """

    custom_alignment = 'fill'

    def __init__(self, pane):
        super().__init__()

        self._pane = pane
        self._hvbox = self.HVBox()
        self._button_speed = self.custom_button_speed
        self._scale_grip = self.custom_scale_grip

        if self.Backward is not None:
            self._backward = self.Backward()
            self._backward.grab_mouse_on_click = True
            self._backward.push_handlers(on_mouse_hold=self.on_backward_click)
            self._hvbox.add(self._backward, 0)

        if self.Grip is not None:
            self._grip = self.Grip()
            self._mover = self.GripMover(self, self._grip)
            self._mover.push_handlers(on_mouse_press=self.on_bar_click)
            self._hvbox.add(self._mover)
        else:
            self._hvbox.add(Spacer())

        if self.Forward is not None:
            self._forward = self.Forward()
            self._forward.grab_mouse_on_click = True
            self._forward.push_handlers(on_mouse_hold=self.on_forward_click)
            self._hvbox.add(self._forward, 0)

        self.add(self._hvbox)

    def on_bar_click(self, x, y, button, modifiers):
        x, y = self._mover.screen_to_child_coords(x,y)

        # Ignore the click if it's on the grip.
        if self._grip.is_under_mouse(x, y):
            return

        # Jump to where the mouse was clicked.
        offset = (x,y) - self._grip.rect.center
        step = offset.dot(self.orientation)
        size = abs(self._mover.unoccupied_size.dot(self.orientation))
        self._pane.scroll_percent(self.orientation * step / size)

    def on_forward_click(self, dt):
        self._pane.scroll(dt * self.button_speed * self.orientation)
        return True

    def on_backward_click(self, dt):
        self._pane.scroll(dt * self.button_speed * -self.orientation)
        return True

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

    def get_scale_grip(self):
        return self._scale_grip

    def set_scale_grip(self, new_scale):
        self._scale_grip = new_scale
        self._repack()

    def _get_scaled_grip_size(self):
        # Reimplement in subclasses to account for the direction of the scroll 
        # bar.
        raise NotImplementedError

@autoprop
class HScrollBar(HVScrollBar):
    HVBox = HBox

    def _get_scaled_grip_size(self):
        width = self._pane.width**2 / self._pane.child.width
        return width, self.height

@autoprop
class VScrollBar(HVScrollBar):
    HVBox = VBox

    def _get_scaled_grip_size(self):
        height = self._pane.height**2 / self._pane.child.height
        return self.width, height

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

