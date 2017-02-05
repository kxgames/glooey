import pyglet
import vecrec
import autoprop

from vecrec import Vector, Rect
from .containers import Bin
from .helpers import *

@autoprop
class Root (Bin):

    def __init__(self, rect, window, batch=None, group=None):
        super().__init__()

        self._parent = self
        self._rect = rect
        self._window = window
        self._batch = batch or pyglet.graphics.Batch()
        self._group = group or pyglet.graphics.Group()

        window.push_handlers(self)

    def repack(self):
        self.claim()

        too_narrow = self.rect.width < self.claimed_width
        too_short = self.rect.height < self.claimed_height

        # Complain if the GUI needs more space than is available in the window.
        if too_narrow or too_short:
            message = "{} is only {}x{}, but its children are {}x{}."
            raise RuntimeError(
                    message.format(
                        self,
                        self.rect.width, self.rect.height,
                        self.claimed_width, self.claimed_height,
            ))

        self.do_resize_children()

    def regroup(self, group):
        super().regroup(group or pyglet.graphics.Group())

    def get_root(self):
        return self

    def get_window(self):
        return self._window

    def get_batch(self):
        return self._batch

    def get_group(self):
        return self._group

    @property
    def is_hidden(self):
        return self._is_hidden


@autoprop
class Gui (Root):

    def __init__(self, window, batch=None, group=None):
        rect = Rect.from_pyglet_window(window)
        super().__init__(rect, window, batch, group)

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        rect = Rect.from_pyglet_window(self.window)
        self.resize(rect)

    def set_cursor(self, image, hot_spot):
        hx, hy = Vector.from_anything(hot_spot)
        cursor = pyglet.window.ImageMouseCursor(image, hx, hy)
        self.window.set_mouse_cursor(cursor)


@autoprop
class PanningGui (Gui):
    """
    A window with mouse exclusivity enabled.  This makes it possible to 
    emit mouse push events, but it also complicates a lot of things.  First of 
    all, an image must be provided so that the mouse can be manually drawn.  
    Second, the mouse coordinates must be manually tracked and fed to the event 
    handlers. 
    """

    def __init__(self, window, cursor, hotspot, batch=None, group=None):
        mouse_group = pyglet.graphics.OrderedGroup(1, parent=group)
        gui_group = pyglet.graphics.OrderedGroup(0, parent=group)

        super().__init__(window, batch, gui_group)
        window.set_exclusive_mouse(True)

        hotspot = vecrec.cast_anything_to_vector(hotspot)
        cursor.anchor_x = hotspot.x
        cursor.anchor_y = hotspot.y

        self.mouse = self.rect.center
        self.shadow_mouse = None
        self.cursor = pyglet.sprite.Sprite(
                cursor, batch=batch, group=mouse_group)

    def do_resize(self, rect):
        self.mouse = rect.center

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
        pass

    def on_mouse_leave(self, x, y):
        # See comment in on_mouse_enter().
        pass

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

        if self.mouse not in self.rect:
            if self.shadow_mouse is None:
                self._start_mouse_pan()

        if self.shadow_mouse is not None:
            if self.mouse in self.rect.get_shrunk(5):
                self._stop_mouse_pan()

        # Move the shadow mouse.

        if self.shadow_mouse is not None:
            self.shadow_mouse += (dx, dy)

            if self.rect.left < self.mouse.x < self.rect.right:
                self.shadow_mouse.x = self.mouse.x
            if self.rect.bottom < self.mouse.y < self.rect.top:
                self.shadow_mouse.y = self.mouse.y

        # Keep the mouse on screen.  This feels like there should be a function 
        # for this in vecrec...

        if self.mouse.x < self.rect.left: self.mouse.x = self.rect.left
        if self.mouse.x > self.rect.right: self.mouse.x = self.rect.right
        if self.mouse.y < self.rect.bottom: self.mouse.y = self.rect.bottom
        if self.mouse.y > self.rect.top: self.mouse.y = self.rect.top

        # Update the mouse sprite.

        self.draw()

    def _start_mouse_pan(self):
        self.shadow_mouse = self.mouse.copy()
        pyglet.clock.schedule_interval(self._update_mouse_pan, 1/60)

    def _stop_mouse_pan(self):
        self.shadow_mouse = None
        pyglet.clock.unschedule(self._update_mouse_pan)

    def _update_mouse_pan(self, dt):
        direction = self.shadow_mouse - self.mouse
        self.dispatch_event('on_mouse_pan', direction, dt)


PanningGui.register_event_type('on_mouse_pan')

@autoprop
class Dialog (Root):
    # Have to set size manually.
    pass


