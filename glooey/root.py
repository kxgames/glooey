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



# Not bad.  I still have to:
#
# 1. Propogate all events.  Make sure this works with buttons inside and 
#    outside the viewport.
# 2. Clip the viewport.
#
# But all the hard stuff is in place!

class GuiWithExclusiveMouse (Root):
    """ A window with mouse exclusivity enabled.  This makes it possible to 
    emit mouse push events, but it also complicates a lot of things.  First of 
    all, an image must be provided so that the mouse can be manually drawn.  
    Second, the x, y coordinates of the mouse must be manually tracked and fed 
    to the event handlers. 
    
    You can specify a group, but things might be screwy if you do.  In 
    particular, the mouse might go behind things in the given group. """

    def __init__(self, window, cursor, hotspot, batch=None, group=None):
        rect = Rect.from_pyglet_window(window)
        mouse_group = pyglet.graphics.OrderedGroup(1, parent=group)
        gui_group = pyglet.graphics.OrderedGroup(0, parent=group)

        Root.__init__(self, rect, window, batch, gui_group)
        window.set_exclusive_mouse(True)

        hotspot = vecrec.cast_anything_to_vector(hotspot)
        cursor.anchor_x = hotspot.x
        cursor.anchor_y = hotspot.y

        self.mouse = rect.center
        self.shadow_mouse = None
        self.mouse_pushing = False
        self.cursor = pyglet.sprite.Sprite(
                cursor, batch=batch, group=mouse_group)

    def draw(self):
        self.cursor.visible = True
        self.cursor.position = self.mouse.tuple

    def undraw(self):
        self.cursor.visible = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse += (dx, dy)

        if self.shadow_mouse is not None:
            self.shadow_mouse += (dx, dy)

        if self.mouse not in self.rect:
            if not self.mouse_pushing:
                self.start_mouse_push()

        if self.mouse_pushing:
            if self.mouse in self.rect.get_shrunk(5):
                self.stop_mouse_push()

        # Keep the mouse on screen.  This should be a vector method.

        if self.mouse.x < self.rect.left: self.mouse.x = self.rect.left
        if self.mouse.x > self.rect.right: self.mouse.x = self.rect.right
        if self.mouse.y < self.rect.bottom: self.mouse.y = self.rect.bottom
        if self.mouse.y > self.rect.top: self.mouse.y = self.rect.top

        # Issue the mouse motion event and draw the mouse.

        Root.on_mouse_motion(self, self.mouse.x, self.mouse.y, dx, dy)
        self.draw()

    def start_mouse_push(self):
        self.mouse_pushing = True
        self.shadow_mouse = self.mouse.copy()
        pyglet.clock.schedule_interval(self.update_mouse_push, 1/60)

    def stop_mouse_push(self):
        self.mouse_pushing = False
        self.shadow_mouse = None
        pyglet.clock.unschedule(self.update_mouse_push)

    def update_mouse_push(self, dt):
        direction = self.shadow_mouse - self.mouse

        self.dispatch_event('on_mouse_push', direction, dt)


GuiWithExclusiveMouse.register_event_type('on_mouse_push')

class Dialog (Root):
    # No mouse push event.
    # Have to set size manually.
    pass



