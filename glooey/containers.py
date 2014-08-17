import pyglet
import vecrec

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
        raise NotImplementedError

    def __len__(self):
        return sum(1 for child in self)


    def claim(self):
        for child in self:
            child.claim()


    def on_attach(self):
        for child in self:
            child.dispatch_event('on_attach')

    def on_detach(self):
        for child in self:
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


    def _attach_child_widget(self, child, attacher):
        child = child.connector
        attacher(child)
        child.parent = self
        self.repack()

    def _detach_child_widget(self, child, detacher):
        child.parent = None
        detacher(child)

    def _update_child_under_mouse(self, x, y):
        previous_child = self.child_under_mouse
        self.child_under_mouse = None

        def yield_previous_child_then_others():
            if previous_child is not None:
                yield previous_child

            yield from (
                    child for child in self
                    if child is not previous_child)

        for child in yield_previous_child_then_others():
            if (x, y) in child:
                self.child_under_mouse = child
                break

        return self.child_under_mouse, previous_child


class Bin (Container):

    def __init__(self, padding=0, align='fill'):
        Container.__init__(self)
        self.child = None
        self.padding = padding
        self.align = align

    def __iter__(self):
        if self.child is not None: yield self.child


    def add(self, child):
        if self.child is not None: self.child.parent = None
        def attacher(child): self.child = child
        self._attach_child_widget(child, attacher)

    def claim(self):
        super(Bin, self).claim()

        self.min_width = 2 * self.padding
        self.min_height = 2 * self.padding

        if self.child is not None:
            self.child.claim()
            self.min_width += self.child.min_width
            self.min_height += self.child.min_height

    def resize(self, rect):
        Container.resize(self, rect)
        if self.child is not None:
            resize_child(self.child, self.align, rect.get_shrunk(self.padding))


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
            translation = -self.viewport.get_child_coords(0, 0)
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(translation.x, translation.y, 0)

        def unset_state(self):
            pyglet.gl.glPopMatrix()


    def __init__(self, sensitivity=3):
        Bin.__init__(self)

        # The panning_vector is the displacement between the bottom-left corner 
        # of this widget and the bottom-left corner of the child widget.

        self._panning_vector = Vector.null()
        self._deferred_center_of_view = None
        self.sensitivity = sensitivity

        # The stencil_group, mask_group, and visible_group members manage the 
        # clipping mask to make sure the child is only visible inside the 
        # viewport.  The panning_group member is used to translate the child in 
        # response to panning events.

        self.stencil_group = drawing.StencilGroup(self.group)
        self.mask_group = drawing.StencilMask(self.stencil_group)
        self.visible_group = drawing.WhereStencilIs(self.stencil_group)
        self.panning_group = Viewport.PanningGroup(self, self.visible_group)

    def add(self, child):
        child.group = self.panning_group
        Bin.add(self, child)

    def claim(self):
        super(Bin, self).claim()

        # The parent claim() method will claim enough space to contain the 
        # entire child widget.  This isn't necessary for the viewport, though, 
        # because the point is to scroll around a bigger widget.

        self.min_width = 2 * self.padding
        self.min_height = 2 * self.padding

    def resize(self, rect):
        Container.resize(self, rect)

        # Allow the child to be whatever size it wants.

        if self.child is not None:
            self.child.resize(self.child.min_rect)

        # Set the center of view if it was previously specified.  The center of 
        # view cannot be directly set until the size of the viewport is known, 
        # but this limitation is hidden from the user by indirectly setting the 
        # center of view as soon as the viewport has a size.

        if self._deferred_center_of_view is not None:
            self.set_center_of_view(self._deferred_center_of_view)

    def draw(self):
        drawing.draw_rectangle(
                self.rect, batch=self.batch, group=self.mask_group)


    def on_attach(self):
        Bin.on_attach(self)
    
        self.stencil_group.parent = self.group

        # If this line raises a pyglet EventException, you may be trying to 
        # attach this widget to a GUI that doesn't support mouse pan events.  
        # See the Viewport documentation for more information.

        self.root.push_handlers(self.on_mouse_pan)

    def on_detach(self):
        self.window.remove_handler(self.on_mouse_pan)
        Bin.on_detach(self)

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_press(self, x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_release(self, x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_motion(self, x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_enter(self, x, y)

    def on_mouse_leave(self, x, y):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_leave(self, x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_drag(self, x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_drag_enter(self, x, y)

    def on_mouse_drag_leave(self, x, y):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_drag_leave(self, x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.get_child_coords(x, y)
        Bin.on_mouse_scroll(self, x, y, scroll_x, scroll_y)

    def on_mouse_pan(self, direction, dt):
        self.panning_vector += direction * self.sensitivity * dt


    @vecrec.accept_anything_as_vector
    def get_child_coords(self, screen_coords):
        viewport_origin = self.rect.bottom_left
        viewport_coords = screen_coords - viewport_origin
        child_origin = self.child.rect.bottom_left
        child_coords = child_origin + self.panning_vector + viewport_coords
        return child_coords

    @vecrec.accept_anything_as_vector
    def get_screen_coords(self, child_coords):
        child_origin = self.child.rect.bottom_left
        viewport_origin = self.rect.bottom_left
        viewport_coords = child_coords - child_origin - self.panning_vector
        screen_coords = view_port_coords + viewport_origin
        return screen_coords

    def get_visible_area(self):
        left, bottom = self.get_child_coords(self.rect.left, self.rect.bottom)
        return Rect.from_dimensions(
                left, bottom, self.rect.width, self.rect.height)

    def get_panning_vector(self):
        return self._panning_vector

    def set_panning_vector(self, vector):
        self._panning_vector = vector

        if self._panning_vector.x < self.child.rect.left:
            self._panning_vector.x = self.child.rect.left

        if self._panning_vector.x > self.child.rect.right - self.rect.width:
            self._panning_vector.x = self.child.rect.right - self.rect.width

        if self._panning_vector.y < self.child.rect.bottom:
            self._panning_vector.y = self.child.rect.bottom

        if self._panning_vector.y > self.child.rect.top - self.rect.height:
            self._panning_vector.y = self.child.rect.top - self.rect.height

    @vecrec.accept_anything_as_vector
    def set_center_of_view(self, child_coords):
        # In order to set the center of view, the size of the viewport widget 
        # is needed.  Unfortunately this information is not available until the 
        # viewport has been attached to a root widget.  To allow this method to 
        # be called at any time, the _focus_point member is used in conjunction 
        # with on_attach() to cache the desired center of view.

        if self.root is None:
            self._deferred_center_of_view = child_coords
        else:
            viewport_center = self.rect.center - self.rect.bottom_left
            self.panning_vector = child_coords - viewport_center
            self._deferred_center_of_view = None


    # Properties (fold)
    panning_vector = property(get_panning_vector, set_panning_vector)


Viewport.register_event_type('on_mouse_pan')

class Grid (Container):

    def __init__(self, rows, cols, padding=0, align='fill'):
        Container.__init__(self)
        self.grid = dict()
        self.padding = padding
        self.align = align
        self.rows = rows
        self.cols = cols

    def __iter__(self):
        yield from self.grid.values()

    def __len__(self):
        return len(self.grid)

    def __getitem__(self, index):
        return self.grid[index]

    def __setitem__(self, index, child):
        row, col = index
        self.add(row, col, child)


    def add(self, row, col, child):
        if not 0 <= row < self.rows: raise IndexError("Row out-of-bounds: row={} num_rows=0..{}".format(row, self.rows))
        if not 0 <= col < self.cols: raise IndexError("Column out-of-bounds: col={} num_cols=0..{}".format(col, self.cols))

        if (row, col) in self.grid: self.grid[row, col].parent = None
        def attacher(child): self.grid[row, col] = child
        self._attach_child_widget(child, attacher)

    def remove(self, row, col):
        def detacher(child): del self.grid[row, col]
        self._attach_child_widget(self.grid[row, col], attacher)

    def claim(self):
        super(Grid, self).claim()

        self.min_width = self.padding * (self.cols + 1)
        self.min_height = self.padding * (self.rows + 1)

        for row in range(self.rows):
            row_height = 0
            for col in range(self.cols):
                if (row, col) in self.grid:
                    child = self.grid[row, col]
                    row_height = max(child.min_height, row_height)
            self.min_height += row_height

        for col in range(self.cols):
            col_width = 0
            for row in range(self.rows):
                if (row, col) in self.grid:
                    child = self.grid[row, col]
                    col_width = max(child.min_width, col_width)
            self.min_width += col_width

    def resize(self, rect):
        super(Grid, self).resize(rect)

        available_width = self.rect.width - self.padding * (self.cols + 1)
        available_height = self.rect.height - self.padding * (self.cols + 1)

        child_width = available_width / self.cols
        child_height = available_height / self.rows

        for row, col in self.grid:
            left = self.rect.left + (child_width * col) + (
                    self.padding * (col + 1))
            bottom = self.rect.bottom + (child_height * (self.rows - row - 1)) + (
                    self.padding * (self.rows - row))
            rect = Rect.from_dimensions(
                    bottom=bottom, left=left,
                    width=child_width, height=child_height)

            child = self.grid[row, col]
            resize_child(child, self.align, rect)


    def yield_cells(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield row, col

class HVBox (Container):

    def __init__(self, padding=0, align='fill'):
        Container.__init__(self)
        self.children = list()
        self.expandable = set()
        self.padding = padding
        self.align = align

    def __iter__(self):
        yield from self.children

    def __len__(self):
        return len(self.children)


    def add(self, child, expand=False):
        self.add_back(child, expand)

    def add_front(self, child, expand=False):
        self.insert(child, 0, expand)

    def add_back(self, child, expand=False):
        self.insert(child, len(self.children), expand)

    def insert(self, child, index, expand=False):
        if expand: self.expandable.add(child)
        self._attach_child_widget(child,
                lambda child: self.children.insert(index, child))

    def remove(self, child):
        self.expandable.discard(child)
        self._detach_child_widget(child,
                lambda child: self.children.remove(child))

    def claim(self):
        raise NotImplementedError

    def resize(self, rect):
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
        self.min_width = 0
        self.min_height = 0
        
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


