from vecrec import Vector, Rect
from .containers import Bin

class Root (Bin):

    def __init__(self, rect, window, batch=None, group=None):
        Bin.__init__(self)

        self.parent = self
        self.rect = rect
        self._window = window
        self._batch = batch or pyglet.graphics.Batch()
        self._group = group

        window.push_handlers(self)

    @property
    def root(self):
        return self

    @property
    def window(self):
        return self._window

    @property
    def batch(self):
        return self._batch

    @property
    def group(self):
        return self._group

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


class Gui (Root):

    def __init__(self, window, batch=None, group=None):
        rect = Rect.from_pyglet_window(window)
        Root.__init__(self, rect, window, batch, group)


class Dialog (Root):
    # No mouse push event.
    # Have to set size manually.
    pass



