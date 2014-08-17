import pyglet
import vecrec

from vecrec import Vector, Rect
from .containers import Bin

class Root (Bin):

    def __init__(self, rect, window, batch=None, group=None):
        Bin.__init__(self)

        self._parent = self
        self._rect = rect
        self._window = window
        self._batch = batch or pyglet.graphics.Batch()
        self._group = group

        window.push_handlers(self)

    def repack(self):
        self.claim()

        too_narrow = self.rect.width < self.min_width
        too_short = self.rect.height < self.min_height

        # Complain if too much space is requested.
        if too_narrow or too_short:
            message = '{}x{} required to render GUI, but the {} is only {}x{}.'
            raise RuntimeError(
                    message.format(
                        self.min_width, self.min_height,
                        self.__class__.__name__,
                        self.rect.width, self.rect.height))

        self.resize(self.rect)

    def get_root(self):
        return self

    def get_window(self):
        return self._window

    def get_batch(self):
        return self._batch

    def get_group(self):
        return self._group


class Gui (Root):

    def __init__(self, window, batch=None, group=None):
        rect = Rect.from_pyglet_window(window)
        Root.__init__(self, rect, window, batch, group)

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        rect = Rect.from_pyglet_window(self.window)
        self.resize(rect)



class PanningGui (Gui):
    """ A window with mouse exclusivity enabled.  This makes it possible to 
    emit mouse push events, but it also complicates a lot of things.  First of 
    all, an image must be provided so that the mouse can be manually drawn.  
    Second, the x, y coordinates of the mouse must be manually tracked and fed 
    to the event handlers. 
    
    You can specify a group, but things might be screwy if you do.  In 
    particular, the mouse might go behind things in the given group. """

    def __init__(self, window, cursor, hotspot, batch=None, group=None):
        mouse_group = pyglet.graphics.OrderedGroup(1, parent=group)
        gui_group = pyglet.graphics.OrderedGroup(0, parent=group)

        super(PanningGui, self).__init__(window, batch, gui_group)
        window.set_exclusive_mouse(True)

        hotspot = vecrec.cast_anything_to_vector(hotspot)
        cursor.anchor_x = hotspot.x
        cursor.anchor_y = hotspot.y

        self.mouse = self.rect.center
        self.shadow_mouse = None
        self.cursor = pyglet.sprite.Sprite(
                cursor, batch=batch, group=mouse_group)

    def resize(self, rect):
        super(PanningGui, self).resize(rect)
        self.mouse = rect.center

    def draw(self):
        self.cursor.visible = True
        self.cursor.position = self.mouse.tuple

    def undraw(self):
        self.cursor.visible = False


    def on_mouse_press(self, x, y, button, modifiers):
        Root.on_mouse_press(self, self.mouse.x, self.mouse.y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        Root.on_mouse_release(self, self.mouse.x, self.mouse.y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self._update_mouse(dx, dy)
        Root.on_mouse_motion(self, self.mouse.x, self.mouse.y, dx, dy)

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
        Root.on_mouse_drag(self, self.mouse.x, self.mouse.y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        Root.on_mouse_drag_enter(self, self.mouse.x, self.mouse.y)

    def on_mouse_drag_leave(self, x, y):
        Root.on_mouse_drag_leave(self, self.mouse.x, self.mouse.y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        Root.on_mouse_scroll(self, self.mouse.x, self.mouse.y, scroll_x, scroll_y)


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

        # Keep the mouse on screen.  This should be a vector method.

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

class Dialog (Root):
    # Have to set size manually.
    pass


