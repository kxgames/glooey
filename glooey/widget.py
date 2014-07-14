import pyglet
from vecrec import Rect

class Widget (pyglet.event.EventDispatcher):

    def __init__(self):
        self.parent = None
        self.connector = self
        self.rect = None
        self.min_width = 0
        self.min_height = 0

    def __contains__(self, point):
        return point in self.rect

    @property
    def root(self):
        return None if self.parent is None else self.parent.root

    @property
    def window(self):
        return self.root.window

    @property
    def batch(self):
        return self.root.batch

    @property
    def group(self):
        return self.root.group

    @property
    def min_rect(self):
        return Rect.from_size(self.min_width, self.min_height)

    def is_attached(self):
        return self.parent is not None

    def attach(self, parent):
        """ Meant to be called by a container widget. """
        assert not self.is_attached()
        self.parent = parent
        self.claim()

    def detach(self):
        """ Meant to be called by a container widget. """
        assert self.is_attached()
        self.undraw()
        self.parent = None

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
        assert self.parent
        self.rect = rect
        self.undraw()
        self.draw()

    def draw(self):
        pass

    def undraw(self):
        pass


Widget.register_event_type('on_mouse_press')
Widget.register_event_type('on_mouse_release')
Widget.register_event_type('on_mouse_motion')
Widget.register_event_type('on_mouse_enter')
Widget.register_event_type('on_mouse_leave')
Widget.register_event_type('on_mouse_drag')
Widget.register_event_type('on_mouse_drag_enter')
Widget.register_event_type('on_mouse_drag_leave')
Widget.register_event_type('on_mouse_scroll')

