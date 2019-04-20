#!/usr/bin/env python3

"""
Top-level widgets that manages the interface between pyglet and glooey.
"""

import pyglet
import vecrec
import autoprop

from vecrec import Vector, Rect
from glooey.widget import Widget
from glooey.containers import Bin, Stack
from glooey.helpers import *

@autoprop
class Root(Stack):
    custom_one_child_gets_mouse = True

    def __init__(self, window, batch=None, group=None):
        super().__init__()

        self.__window = window
        self.__batch = batch or pyglet.graphics.Batch()
        self._regroup(group)
        self.__spurious_leave_event = False

        window.push_handlers(self)

    def on_mouse_enter(self, x, y):
        # For some reason, whenever the mouse is clicked, X11 generates a 
        # on_mouse_leave event followed by a on_mouse_enter event.  There's no 
        # way to tell whether or not that happened in this handler alone, so we 
        # check a flag that would be set in on_mouse_leave() if a spurious 
        # event was detected.  If the event is spurious, reset the flag, ignore 
        # the event, and stop it from propagating.

        if self.__spurious_leave_event:
            self.__spurious_leave_event = False
            return True
        else:
            super().on_mouse_enter(x, y)

    def on_mouse_leave(self, x, y):
        # For some reason, whenever the mouse is clicked, X11 generates a 
        # on_mouse_leave event followed by a on_mouse_enter event.  We can tell 
        # that this is happening in this handler because the mouse coordinates 
        # will still be under the widget.  In this case, set a flag so 
        # on_mouse_enter() will know to ignore the spurious event to follow and 
        # to stop it from propagating.

        if self.is_under_mouse(x, y):
            self.__spurious_leave_event = True
            return True
        else:
            super().on_mouse_leave(x, y)

    def get_root(self):
        return self

    def get_parent(self):
        return self

    def get_window(self):
        return self.__window

    def get_batch(self):
        return self.__batch

    def get_territory(self):
        raise NotImplementedError

    @update_function
    def _repack(self):
        self._claim()

        too_narrow = self.territory.width < self.claimed_width
        too_short = self.territory.height < self.claimed_height

        # Complain if the root widget needs more space than it claimed.
        if too_narrow or too_short:
            message = "{} is only {}x{}, but its children are {}x{}."
            raise RuntimeError(
                    message.format(
                        self,
                        self.territory.width, self.territory.height,
                        self.claimed_width, self.claimed_height,
            ))

        self._resize(self.territory)

    def _regroup(self, group):
        # We need to replace None with an actual group, because glooey 
        # interprets None as "my parent hasn't given me a group yet."
        super()._regroup(group or pyglet.graphics.Group())


@autoprop
class Gui(Root):
    custom_clear_before_draw = True

    def __init__(self, window, *, cursor=None, hotspot=None,
            clear_before_draw=None, batch=None, group=None):

        super().__init__(window, batch, group)

        # Set the cursor, if the necessary arguments were given.
        if cursor and not hotspot:
            raise ValueError("Specified cursor but not hotspot.")
        if hotspot and not cursor:
            raise ValueError("Specified hotspot but not cursor.")
        if cursor and hotspot:
            self.set_cursor(cursor, hotspot)

        # Disable clearing the window on each draw.
        self.clear_before_draw = first_not_none((
            clear_before_draw, self.custom_clear_before_draw))

    def on_draw(self):
        if self.clear_before_draw:
            self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        # Make sure the window actually changed size before starting a repack.  
        # We compare against `self.rect` (which requires subtracting the 
        # padding from the given width and height) instead of `self.territory` 
        # so that changing the padding triggers a repack like it should.
        width -= self.left_padding + self.right_padding
        height -= self.top_padding + self.bottom_padding
        if self.rect and self.rect.size != (width, height):
            self._repack()

    def get_territory(self):
        return Rect.from_pyglet_window(self.window)
        
    def set_cursor(self, image, hot_spot):
        hx, hy = Vector.from_anything(hot_spot)
        cursor = pyglet.window.ImageMouseCursor(image, hx, hy)
        self.window.set_mouse_cursor(cursor)


@autoprop
@register_event_type('on_mouse_pan')
class PanningGui(Gui):
    """
    A window that emits ``on_mouse_pan`` events when the mouse is off-screen.
    
    `PanningGui` is typically used in conjunction with `Viewport`, which is a 
    container that scrolls its children in response to ``on_mouse_pan`` events.  
    Together, these two widgets allow the user to scroll widgets (e.g. a game 
    map) by moving the mouse off the screen, which is a common motif in games.

    The ``on_mouse_pan`` event fires continuously (e.g. 60 Hz) when the mouse 
    is off the screen.  Each event specifies how far off the screen the mouse 
    is in the vertical and horizontal dimensions, and how much time elapsed 
    since the last event fired.

    Normally, a window doesn't receive information about the mouse unless the 
    mouse is within the boundaries of that window.  In order for `PanningGui` 
    to break this rule and keep track of the mouse while it is outside the 
    window, it has to enable `mouse exclusivity`__.  One consequence of this is 
    that, unlike with `Gui`, a cursor image must be provided.

    __ https://pyglet.readthedocs.io/en/pyglet-1.2-maintenance/programming_guide/mouse.html#mouse-exclusivity
    """

    def __init__(self, window, cursor, hotspot, *, batch=None, group=None):
        mouse_group = pyglet.graphics.OrderedGroup(1, parent=group)
        gui_group = pyglet.graphics.OrderedGroup(0, parent=group)

        super().__init__(window, batch=batch, group=gui_group)
        window.set_exclusive_mouse(True)

        # Where the mouse is.  Because mouse exclusivity is enabled, we have to 
        # keep track of this ourselves.
        self.mouse = self.territory.center

        # Where the mouse would be, if it wasn't confined to the window.  The 
        # difference between `self.mouse` and `self.shadow_mouse` gives the 
        # direction of each ``on_mouse_pan`` event that gets fired.
        self.shadow_mouse = None

        # Because mouse exclusivity is enabled, we have to provide an image for 
        # the cursor.
        hotspot = vecrec.cast_anything_to_vector(hotspot)
        cursor.anchor_x = hotspot.x
        cursor.anchor_y = hotspot.y

        self.cursor = pyglet.sprite.Sprite(
                cursor, batch=self.batch, group=mouse_group)

    def do_resize(self):
        self.mouse = self.territory.center

    def do_draw(self):
        self.cursor.visible = True
        self.cursor.position = self.mouse.tuple

    def do_undraw(self):
        self.cursor.visible = False

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(self.mouse.x, self.mouse.y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        super().on_mouse_release(self.mouse.x, self.mouse.y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self._update_mouse(dx, dy)
        super().on_mouse_motion(self.mouse.x, self.mouse.y, dx, dy)

    def on_mouse_enter(self, x, y):
        # The mouse never really enters or exits a window with mouse 
        # exclusivity enabled, so mouse_enter and mouse_exits events should 
        # never get triggered.  However, there is at least one scenario where 
        # pyglet will do just that.
        # 
        # This scenario can be triggered by instantly moving the window by more 
        # than half of its width or height.  The issue is that, with mouse 
        # exclusivity enabled, pyglet keeps the mouse in the center of the 
        # screen.  If the window is moved far enough in one frame to put the 
        # old mouse position outside the window, a spurious set of mouse_exit 
        # and mouse_enter events get triggered.
        # 
        # The solution to this problem is simply to ignore mouse_enter and 
        # mouse_exit events for PanningGui objects.
        return True

    def on_mouse_leave(self, x, y):
        # See comment in on_mouse_enter().
        return True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._update_mouse(dx, dy)
        super().on_mouse_drag(self.mouse.x, self.mouse.y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        super().on_mouse_drag_enter(self.mouse.x, self.mouse.y)

    def on_mouse_drag_leave(self, x, y):
        super().on_mouse_drag_leave(self.mouse.x, self.mouse.y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(self.mouse.x, self.mouse.y, scroll_x, scroll_y)

    def _update_mouse(self, dx, dy):
        self.mouse += (dx, dy)

        # Decide whether or to start or stop panning.

        if self.mouse not in self.territory:
            if self.shadow_mouse is None:
                self._start_mouse_pan()

        if self.shadow_mouse is not None:
            if self.mouse in self.territory.get_shrunk(5):
                self._stop_mouse_pan()

        # Move the shadow mouse.

        if self.shadow_mouse is not None:
            self.shadow_mouse += (dx, dy)

            if self.territory.left < self.mouse.x < self.territory.right:
                self.shadow_mouse.x = self.mouse.x
            if self.territory.bottom < self.mouse.y < self.territory.top:
                self.shadow_mouse.y = self.mouse.y

        # Keep the mouse on screen.  It feels like there should be a function 
        # for this in vecrec...

        if self.mouse.x < self.territory.left:
            self.mouse.x = self.territory.left
        if self.mouse.x > self.territory.right:
            self.mouse.x = self.territory.right
        if self.mouse.y < self.territory.bottom:
            self.mouse.y = self.territory.bottom
        if self.mouse.y > self.territory.top:
            self.mouse.y = self.territory.top

        # Update the mouse sprite.

        self._draw()

    def _start_mouse_pan(self):
        self.shadow_mouse = self.mouse.copy()
        pyglet.clock.schedule_interval(self._update_mouse_pan, 1/60)

    def _stop_mouse_pan(self):
        self.shadow_mouse = None
        pyglet.clock.unschedule(self._update_mouse_pan)

    def _update_mouse_pan(self, dt):
        direction = self.shadow_mouse - self.mouse
        self.dispatch_event('on_mouse_pan', direction, dt)

