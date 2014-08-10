import pyglet
from vecrec import Vector, Rect
from .widget import Widget
from . import drawing

def center_within_rect(child_rect, parent_rect):
    child_rect.center = parent_rect.center

placement_functions = { # (fold)
        'fill': lambda child_rect, parent_rect: child_rect.set(parent_rect),
        'center': center_within_rect,
}

def resize_child(child, key_or_function, box_rect, child_rect=None):
    try:
        placement_function = placement_functions[key_or_function]
    except KeyError:
        placement_function = key_or_function

    if child_rect is None:
        child_rect = child.min_rect

    placement_function(child_rect, box_rect)
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
        child.parent = self
        self.repack()

    def remove(self, child):
        child.parent = None
        self.children.remove(child)


    def on_attach(self):
        for child in self.children:
            child.dispatch_event('on_attach')

    def on_detach(self):
        for child in self.children:
            child.dispatch_event('on_detach')

    def on_mouse_press(self, x, y, button, modifiers):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event(
                    'on_mouse_press', x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event(
                    'on_mouse_release', x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        current_child, previous_child = self._update_child_under_mouse(x, y)

        if previous_child is not None:
            if previous_child is not current_child:
                previous_child.dispatch_event('on_mouse_leave', x, y)

        if current_child is not None:
            if current_child is not previous_child:
                current_child.dispatch_event('on_mouse_enter', x, y)

            current_child.dispatch_event('on_mouse_motion', x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        child, previous_child = self._update_child_under_mouse(x, y)
        assert previous_child is None
        if child is not None: child.dispatch_event('on_mouse_enter', x, y)

    def on_mouse_leave(self, x, y):
        if self.child_under_mouse is not None:
            self.child_under_mouse.dispatch_event('on_mouse_leave', x, y)
        self.child_under_mouse = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        current_child, previous_child = self._update_child_under_mouse(x, y)

        if previous_child is not None:
            if previous_child is not current_child:
                previous_child.dispatch_event('on_mouse_drag_leave', x, y)

        if current_child is not None:
            if current_child is not previous_child:
                current_child.dispatch_event('on_mouse_drag_enter', x, y)

            current_child.dispatch_event(
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
            self.child.parent = None

        self.child = child.get_connector()
        self.child.parent = self
        self.repack()

    def claim(self):
        self.min_width = 2 * self.padding
        self.min_height = 2 * self.padding

        if self.child is not None:
            self.child.claim()
            self.min_width += self.child.min_width
            self.min_height += self.child.min_height

    def resize(self, rect):
        Widget.resize(self, rect)
        if self.child is not None:
            resize_child(self.child, self.align, rect.get_shrunk(self.padding))


    def on_attach(self):
        if self.child is not None:
            self.child.dispatch_event('on_attach')

    def on_detach(self):
        if self.child is not None:
            self.child.dispatch_event('on_detach')

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

    def __init__(self, padding=0, align='fill'):
        Bin.__init__(self, padding, align)
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


class Viewport (Bin):

    class PanningGroup (pyglet.graphics.Group):

        # Might want to have this class derive from OrderedGroup, to put the 
        # viewport behind the gui.

        def __init__(self, viewport, parent=None):
            super(Viewport.PanningGroup, self).__init__(parent)
            self.viewport = viewport

        def set_state(self):
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(
                    -self.viewport.offset.x, -self.viewport.offset.y, 0)

        def unset_state(self):
            pyglet.gl.glPopMatrix()


    def __init__(self, sensitivity=3, clip=False):
        Bin.__init__(self)
        self.offset = Vector.null()
        self.sensitivity = sensitivity
        self.panning_group = Viewport.PanningGroup(self)
        self.enable_clipping = clip

    def wrap(self, child):
        # Give child a group that's hooked up to:
        # 1. translate on my command
        # 2. get clipped.
        child.group = self.panning_group
        Bin.wrap(self, child)

    def claim(self):
        self.min_width = 2 * self.padding
        self.min_height = 2 * self.padding

        if self.child is not None:
            self.child.claim()

    def resize(self, rect):
        Widget.resize(self, rect)
        if self.child is not None:
            self.child.resize(self.child.min_rect)

    def draw(self):
        # update clipping mask.
        pass


    def on_attach(self):
        Bin.on_attach(self)
        self.panning_group.parent = self.group

        # If this line raises a pyglet EventException, you may be trying to 
        # attach this widget to a GUI that doesn't support mouse pan events.  
        # See the Viewport documentation for more information.

        self.root.push_handlers(self.on_mouse_pan)

    def on_detach(self):
        self.window.remove_handler(self.on_mouse_pan)
        Bin.on_detach(self)

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.offset + (x, y)
        Bin.on_mouse_press(self, x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.offset + (x, y)
        Bin.on_mouse_release(self, x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.offset + (x, y)
        Bin.on_mouse_motion(self, x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        x, y = self.offset + (x, y)
        Bin.on_mouse_enter(self, x, y)

    def on_mouse_leave(self, x, y):
        x, y = self.offset + (x, y)
        Bin.on_mouse_leave(self, x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = self.offset + (x, y)
        Bin.on_mouse_drag(self, x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        x, y = self.offset + (x, y)
        Bin.on_mouse_drag_enter(self, x, y)

    def on_mouse_drag_leave(self, x, y):
        x, y = self.offset + (x, y)
        Bin.on_mouse_drag_leave(self, x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.offset + (x, y)
        Bin.on_mouse_scroll(self, x, y, scroll_x, scroll_y)

    def on_mouse_pan(self, direction, dt):
        self.offset += direction * self.sensitivity * dt

        # This should be a vector method.

        if self.offset.x < self.child.rect.left:
            self.offset.x = self.child.rect.left

        if self.offset.x > self.child.rect.right - self.rect.width:
            self.offset.x = self.child.rect.right - self.rect.width

        if self.offset.y < self.child.rect.bottom:
            self.offset.y = self.child.rect.bottom

        if self.offset.y > self.child.rect.top - self.rect.height:
            self.offset.y = self.child.rect.top - self.rect.height


Viewport.register_event_type('on_mouse_pan')


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

    def claim(self):
        raise NotImplementedError

    def resize(self):
        raise NotImplementedError


    _dimensions = {     # (fold)
            'horizontal': ('width', 'height'),
            'vertical':   ('height', 'width'),
    }
    _coordinates = {    # (fold)
            'horizontal': ('left', 'top'),
            'vertical':   ('top', 'left'),
    }


    def _claim(self, orientation):
        
        # Account for children

        for child in self.children:
            child.claim()

            if orientation == 'horizontal':
                self.min_width += child.min_width
                self.min_height = max(self.min_height, child.min_height)
            elif orientation == 'vertical':
                self.min_height += child.min_height
                self.min_width = max(self.min_width, child.min_width)
            else:
                raise ValueError("Unknown orientation: {}".format(orientation))

        # Account for padding

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


