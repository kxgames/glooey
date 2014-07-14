from vecrec import Rect
from .widget import Widget
from . import drawing

def center_within_rect(child_rect, parent_rect):
    child_rect.center = parent_rect.center

placement_algorithms = { # (fold)
        'fill': lambda child_rect, parent_rect: child_rect.set(parent_rect),
        'center': center_within_rect,
}

def resize_child(child, key_or_function, box_rect, child_rect=None):
    try:
        place_rect = placement_algorithms[key_or_function]
    except KeyError:
        place_rect = key_or_function

    if child_rect is None:
        child_rect = child.min_rect

    place_rect(child_rect, box_rect)
    child.resize(child_rect)


class Container (Widget):

    def __init__(self):
        Widget.__init__(self)
        self.children = []
        self.child_under_mouse = None
        self.min_width = 0
        self.min_height = 0

    def __iter__(self):
        yield from self.children

    def __len__(self):
        return len(self.children)

    def insert(self, child, index=None):
        child = child.connector
        if index is None: index = len(self.children)
        self.children.insert(index, child)
        child.attach(self)
        self.repack()

    def remove(self, child):
        child.detach()
        self.children.remove(child)

    def claim(self):
        self.min_width = sum(x.min_width for x in self.children)
        self.min_height = sum(x.min_height for x in self.children)


    def on_mouse_press(self, x, y, button, modifiers):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event(
                    'on_mouse_release', x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event(
                    'on_mouse_release', x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        child, previous_child = self._update_child_under_mouse(x, y)

        if child is not None:
            if child is not previous_child:
                if previous_child is not None:
                    previous_child.dispatch_event('on_mouse_leave', x, y)
                child.dispatch_event('on_mouse_enter', x, y)

            child.dispatch_event('on_mouse_motion', x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        child, previous_child = self._update_child_under_mouse(x, y)
        assert previous_child is None
        if child is not None: child.dispatch_event('on_mouse_enter', x, y)

    def on_mouse_leave(self, x, y):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event('on_mouse_leave', x, y)
        self.child_under_mouse = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        child, previous_child = self._update_child_under_mouse(x, y)

        if child is not None:
            if child is not previous_child:
                if previous_child is not None:
                    previous_child.dispatch_event('on_mouse_drag_leave', x, y)
                child.dispatch_event('on_mouse_drag_enter', x, y)

            child.dispatch_event(
                    'on_mouse_drag', x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        child, previous_child = self._update_child_under_mouse(x, y)
        assert previous_child is None
        if child is not None: child.dispatch_event('on_mouse_drag_enter', x, y)

    def on_mouse_drag_leave(self, x, y):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event('on_mouse_drag_leave', x, y)
        self.child_under_mouse = None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event(
                    'on_mouse_scroll', x, y, scroll_x, scroll_y)


    def _update_child_under_mouse(self, x, y):
        previous_child = self.child_under_mouse
        self.child_under_mouse = None

        def yield_previous_child_then_others():
            if previous_child is not None:
                yield previous_child

            yield from (
                    child for child in self.children
                    if child is not previous_child)

        for child in yield_previous_child_then_others():
            if (x, y) in child:
                self.child_under_mouse = child
                break

        return self.child_under_mouse, previous_child


class Bin (Widget):

    def __init__(self, padding=0, align='fill'):
        Widget.__init__(self)
        self.child = None
        self.child_under_mouse = False
        self.padding = padding
        self.align = align

    def wrap(self, child):
        if self.child is not None:
            child.detach()

        self.child = child.connector
        self.child.attach(self)
        self.repack()

    def claim(self):
        self.min_width = self.child.min_width + 2 * self.padding
        self.min_height = self.child.min_height + 2 * self.padding

    def resize(self, rect):
        Widget.resize(self, rect)
        if self.child is not None:
            resize_child(self.child, self.align, rect.get_shrunk(self.padding))


    def on_mouse_press(self, x, y, button, modifiers):
        if self.child_under_mouse:
            self.child.dispatch_event(
                    'on_mouse_press', x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.child_under_mouse:
            self.child.dispatch_event(
                    'on_mouse_release', x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        child_previously_under_mouse = self.child_under_mouse
        self.child_under_mouse = (x, y) in self.child

        if self.child_under_mouse:
            if not child_previously_under_mouse:
                self.child.dispatch_event('on_mouse_enter', x, y)

            self.child.dispatch_event('on_mouse_motion', x, y, dx, dy)

        else:
            if child_previously_under_mouse:
                self.child.dispatch_event('on_mouse_leave', x, y)

    def on_mouse_enter(self, x, y):
        self.child_under_mouse = (x, y) in self.child
        if self.child_under_mouse:
            self.child.dispatch_event('on_mouse_enter', x, y)

    def on_mouse_leave(self, x, y):
        if self.child_under_mouse:
            self.child.dispatch_event('on_mouse_leave', x, y)
        self.child_under_mouse = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        child_previously_under_mouse = self.child_under_mouse
        self.child_under_mouse = (x, y) in self.child

        if self.child_under_mouse:
            if not child_previously_under_mouse:
                self.child.dispatch_event('on_mouse_drag_enter', x, y)

            self.child.dispatch_event(
                    'on_mouse_drag', x, y, dx, dy, buttons, modifiers)
        else:
            if child_previously_under_mouse:
                self.child.dispatch_event('on_mouse_drag_leave', x, y)

    def on_mouse_drag_enter(self, x, y):
        self.child_under_mouse = (x, y) in self.child
        if self.child_under_mouse:
            self.child.dispatch_event('on_mouse_drag_enter', x, y)

    def on_mouse_drag_leave(self, x, y):
        if self.child_under_mouse:
            self.child.dispatch_event('on_mouse_drag_leave', x, y)
        self.child_under_mouse = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.child_under_mouse:
            self.child.dispatch_event(
                    'on_mouse_scroll', x, y, scroll_x, scroll_y)


class Frame (Bin):

    def __init__(self):
        Bin.__init__(self)
        self.edge_image = None
        self.edge_orientation = None
        self.corner_image = None
        self.corner_orientation = None
        self.vertex_lists = ()

    def set_edge(self, image, orientation='left', autopad=True):
        self.edge_image = image
        self.edge_orientation = orientation

        if autopad and orientation in ('top', 'bottom'):
            self.padding = image.height
        if autopad and orientation in ('left', 'right'):
            self.padding = image.width

    def set_corner(self, image, orientation='top left'):
        if self.edge_image is None:
            raise RuntimeError("Frame.set_corner() cannot be called until Frame.set_edge() has been.")

        self.corner_image = image
        self.corner_orientation = orientation

    def draw(self):
        if self.edge_image is None:
            raise ValueError("Must call Frame.set_edge() before Frame.draw().")

        self.vertex_lists = drawing.draw_frame(
                self.rect,
                self.edge_image, self.edge_orientation,
                self.corner_image, self.corner_orientation,
                batch=self.batch, group=self.group, usage='static')

    def undraw(self):
        for vertex_list in self.vertex_lists:
            vertex_list.delete()
        self.vertex_lists = ()



class HVBox (Container):

    def __init__(self, padding=0, align='fill'):
        Container.__init__(self)
        self.padding = padding
        self.align = align
        self.expandable = set()

    def add_front(self, child, expand=False):
        if expand: self.expandable.add(child)
        Container.insert(self, child, 0)

    def add_back(self, child, expand=False):
        if expand: self.expandable.add(child)
        Container.insert(self, child)

    add = add_back

    def remove(self, child):
        self.expandable.discard(child)
        Container.remove(self, child)


    _dimensions = {     # (fold)
            'horizontal': ('width', 'height'),
            'vertical':   ('height', 'width'),
    }
    _coordinates = {    # (fold)
            'horizontal': ('left', 'top'),
            'vertical':   ('top', 'left'),
    }


    def _claim(self, orientation):
        Container.claim(self)

        primary_padding = self.padding * (1 + len(self))
        secondary_padding = self.padding * 2

        if orientation == 'horizontal':
            self.min_width += primary_padding
            self.min_height += secondary_padding
        elif orientation == 'vertical':
            self.min_width += secondary_padding
            self.min_height += primary_padding
        else:
            raise ValueError("Unknown orientation: {}".format(orientation))

    def _resize(self, rect, orientation):
        Container.resize(self, rect)
        
        if not self.children:
            return

        dimension = self._dimensions[orientation]
        coordinate = self._coordinates[orientation]
        min_dimension = tuple('min_' + x for x in dimension)

        # Figure out how much space is available for expandable children.

        available_space = getattr(rect, dimension[0]) - self.padding

        for child in self.children:
            available_space -= getattr(child, min_dimension[0]) + self.padding

        # Resize each child.

        cursor, anchor = self._place_cursor(rect, orientation)

        for child in self.children:
            box_coord_0 = cursor
            box_coord_1 = anchor
            box_dimension_0 = getattr(child, min_dimension[0])
            box_dimension_1 = getattr(rect, dimension[1]) - 2 * self.padding

            if child in self.expandable:
                box_dimension_0 += available_space / len(self.expandable)

            cursor = self._update_cursor(cursor, box_dimension_0, orientation)

            box_rect = Rect(0, 0, 0, 0)
            setattr(box_rect, dimension[0], box_dimension_0)
            setattr(box_rect, dimension[1], box_dimension_1)
            setattr(box_rect, coordinate[0], box_coord_0)
            setattr(box_rect, coordinate[1], box_coord_1)

            child_rect = Rect(0, 0, 0, 0)
            setattr(child_rect, dimension[0], box_dimension_0)
            setattr(child_rect, dimension[1], getattr(child, min_dimension[1]))

            resize_child(child, self.align, box_rect, child_rect)

    def _place_cursor(self, rect, orientation):
        top = rect.top - self.padding
        left = rect.left + self.padding

        if orientation == 'horizontal': return left, top
        elif orientation == 'vertical': return top, left
        else: raise ValueError("Unknown orientation: {}".format(orientation))

    def _update_cursor(self, cursor, child_size, orientation):
        if orientation == 'horizontal':
            return cursor + child_size + self.padding
        elif orientation == 'vertical':
            return cursor - child_size - self.padding
        else:
            raise ValueError("Unknown orientation: {}".format(orientation))


class HBox (HVBox):

    def claim(self):
        super(HBox, self)._claim('horizontal')

    def resize(self, rect):
        super(HBox, self)._resize(rect, 'horizontal')


class VBox (HVBox):

    def claim(self):
        super(VBox, self)._claim('vertical')

    def resize(self, rect):
        super(VBox, self)._resize(rect, 'vertical')


