import pyglet
from vecrec import Rect

class Widget (pyglet.event.EventDispatcher):

    def __init__(self):
        self._parent = None
        self._group = None
        self._connector = self
        self._rect = None
        self.min_width = 0
        self.min_height = 0

    def __contains__(self, point):
        return point in self.rect


    def claim(self):
        """ 
        Opportunity to set min_width and min_height before repacking.
        """
        pass

    def repack(self, force=False):
        if self.root is None:
            return

        self.claim()

        too_narrow = self.rect.width < self.min_width
        too_short = self.rect.height < self.min_height

        # If the widget is too small, repack its parent to make more space.
        if too_narrow or too_short or force:
            self.parent.repack()

        # Otherwise, stop recursing and resize the widget.
        else:
            self.resize(self.rect)

    def resize(self, rect):
        assert self.parent is not None, "self={} self.parent={}".format(self, self.parent)
        self._rect = rect
        self.draw()

    def draw(self):
        pass

    def undraw(self):
        pass


    def get_parent(self):
        return self._parent

    def get_root(self):
        return None if self._parent is None else self._parent.root

    def get_window(self):
        return self.root.window

    def get_batch(self):
        return self.root.batch

    def get_group(self):
        if self._group is not None: return self._group
        if self.parent is not None: return self.parent.group
        return None

    def get_connector(self):
        return self._connector

    def get_rect(self):
        return self._rect

    def get_min_rect(self):
        return Rect.from_size(self.min_width, self.min_height)

    def set_parent(self, parent):
        if self.parent is not None and self.parent.root is not None:
            self.dispatch_event('on_detach')

        self._parent = parent

        if self.parent is not None and self.parent.root is not None:
            self.dispatch_event('on_attach')

    def set_group(self, group):
        self._group = group

    def set_connector(self, connector):
        assert self._connector is None
        self._connector = connector

    def is_attached(self):
        return self.parent is not None


    # Properties (fold)

    parent = property(
            lambda self: self.get_parent(),
            lambda self, parent: self.set_parent(parent))
    root = property(
            lambda self: self.get_root())
    window = property(
            lambda self: self.get_window())
    batch = property(
            lambda self: self.get_batch())
    group = property(
            lambda self: self.get_group(),
            lambda self, group: self.set_group(group))
    connector = property(
            lambda self: self.get_connector(),
            lambda self, conn: self.set_connector(conn))
    rect = property(
            lambda self: self.get_rect())
    min_rect = property(
            lambda self: self.get_min_rect())


Widget.register_event_type('on_attach')
Widget.register_event_type('on_detach')
Widget.register_event_type('on_mouse_press')
Widget.register_event_type('on_mouse_release')
Widget.register_event_type('on_mouse_motion')
Widget.register_event_type('on_mouse_enter')
Widget.register_event_type('on_mouse_leave')
Widget.register_event_type('on_mouse_drag')
Widget.register_event_type('on_mouse_drag_enter')
Widget.register_event_type('on_mouse_drag_leave')
Widget.register_event_type('on_mouse_scroll')

