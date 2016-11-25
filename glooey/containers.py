""" 
Widgets whose primary role is to contain other widgets.  Most of these widgets 
don't draw anything themselves, they just position children widgets.
"""

import pyglet
import vecrec

from vecrec import Vector, Rect
from collections import defaultdict
from . import drawing
from .widget import Widget
from .helpers import *

def fill(child_rect, parent_rect):
    child_rect.set(parent_rect)

def top_left(child_rect, parent_rect):
    child_rect.top_left = parent_rect.top_left

def top_center(child_rect, parent_rect):
    child_rect.top_center = parent_rect.top_center

def top_right(child_rect, parent_rect):
    child_rect.top_right = parent_rect.top_right

def center_left(child_rect, parent_rect):
    child_rect.center_left = parent_rect.center_left

def center(child_rect, parent_rect):
    child_rect.center = parent_rect.center

def center_right(child_rect, parent_rect):
    child_rect.center_right = parent_rect.center_right

def bottom_left(child_rect, parent_rect):
    child_rect.bottom_left = parent_rect.bottom_left

def bottom_center(child_rect, parent_rect):
    child_rect.bottom_center = parent_rect.bottom_center

def bottom_right(child_rect, parent_rect):
    child_rect.bottom_right = parent_rect.bottom_right

placement_functions = {
        'fill': fill,
        'top_left': top_left,
        'top_center': top_center,
        'top_right': top_right,
        'center_left': center_left,
        'center': center,
        'center_right': center_right,
        'bottom_left': bottom_left,
        'bottom_center': bottom_center,
        'bottom_right': bottom_right,
}

def place_child_in_box(child, box_rect, key_or_function, child_rect=None):
    try:
        placement_function = placement_functions[key_or_function]
    except KeyError:
        placement_function = key_or_function

    if child_rect is None:
        child_rect = child.min_rect

    placement_function(child_rect, box_rect)
    child.resize(child_rect)


class Bin (Widget):

    def __init__(self, padding=0, placement='fill'):
        super().__init__()
        self._child = None
        self._padding = padding
        self._placement = placement

    def add(self, child):
        if self._child is not None:
            self._detach_child(self._child)

        self._child = self._attach_child(child)
        assert self._num_children == 1
        self._resize_and_regroup_children()

    def clear(self):
        self._detach_child(self.child)
        self.child = None
        assert self._num_children == 0
        self._resize_and_regroup_children()

    def get_child(self):
        return self._child

    child = late_binding_property(get_child)

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding):
        self._padding = new_padding
        self.repack()

    padding = late_binding_property(get_padding, set_padding)

    def get_placement(self):
        return self._placement

    def set_placement(self, new_placement):
        self._placement = new_placement
        self.repack()

    placement = late_binding_property(get_placement, set_placement)

    def do_claim(self):
        min_width = 2 * self.padding
        min_height = 2 * self.padding

        if self.child is not None:
            min_width += self.child.min_width
            min_height += self.child.min_height

        return min_width, min_height

    def do_resize_children(self):
        if self.child is not None:
            place_child_in_box(
                    self.child,
                    self.rect.get_shrunk(self.padding),
                    self.placement)


class Frame (Bin):

    def __init__(self, padding=0, placement='fill'):
        super().__init__(padding, placement)
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

    def do_draw(self):
        if self.edge_image is None:
            raise ValueError("Must call Frame.set_edge() before Frame.draw().")

        self.vertex_lists = drawing.draw_frame(
                self.rect,
                self.edge_image, self.edge_orientation,
                self.corner_image, self.corner_orientation,
                batch=self.batch, group=self.group, usage='static')

    def do_undraw(self):
        for vertex_list in self.vertex_lists:
            vertex_list.delete()
        self.vertex_lists = ()


class Viewport (Bin):

    class PanningGroup (pyglet.graphics.Group):

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
        super().__init__()

        # The panning_vector is the displacement between the bottom-left corner 
        # of this widget and the bottom-left corner of the child widget.

        self._panning_vector = Vector.null()
        self._deferred_center_of_view = None
        self.sensitivity = sensitivity

        # The stencil_group, mask_group, and visible_group members manage the 
        # clipping mask to make sure the child is only visible inside the 
        # viewport.  The panning_group member is used to translate the child in 
        # response to panning events.

        self.stencil_group = None
        self.mask_group = None
        self.visible_group = None
        self.panning_group = None
        self.mask_artist = None

    def do_claim(self):
        # The widget being displayed in the viewport can claim however much 
        # space it wants.  The viewport can be much smaller, because the whole 
        # point is to scroll around a bigger widget, so it will just claim 
        # enough space for its padding.
        return 2 * self.padding, 2 * self.padding

    def do_resize(self):
        # Set the center of view if it was previously specified.  The center of 
        # view cannot be directly set until the size of the viewport is known, 
        # but this limitation is hidden from the user by indirectly setting the 
        # center of view as soon as the viewport has a size.
        if self._deferred_center_of_view is not None:
            self.set_center_of_view(self._deferred_center_of_view)

    def do_resize_children(self):
        # Make the child whatever size it wants to be.
        if self.child is not None:
            self.child.resize(self.child.min_rect)

    def do_regroup(self):
        self.stencil_group = drawing.StencilGroup(self.group)
        self.mask_group = drawing.StencilMask(self.stencil_group)
        self.visible_group = drawing.WhereStencilIs(self.stencil_group)
        self.panning_group = Viewport.PanningGroup(self, self.visible_group)

        if self.mask_artist is not None:
            self.mask_artist.group = self.mask_group

    def do_regroup_children(self):
        self.child.regroup(self.panning_group)

    def do_draw(self):
        if self.mask_artist is None:
            self.mask_artist = drawing.Rectangle(
                    self.rect,
                    batch=self.batch,
                    group=self.mask_group)

        self.mask_artist.rect = self.rect

    def do_undraw(self):
        if self.mask_artist is not None:
            self.mask_artist.delete()

    def on_attach_to_gui(self):

        # If this line raises a pyglet EventException, you're probably trying 
        # to attach this widget to a GUI that doesn't support mouse pan events.  
        # See the Viewport documentation for more information.

        self.root.push_handlers(self.on_mouse_pan)

    def on_detach_from_gui(self):
        self.window.remove_handler(self.on_mouse_pan)

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_motion(x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_enter(x, y)

    def on_mouse_leave(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_leave(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_drag_enter(x, y)

    def on_mouse_drag_leave(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_drag_leave(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

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
        # be called at any time, the _deferred_center_of_view member is used in 
        # conjunction with do_resize() to cache the desired center of view.

        if self.rect is None:
            self._deferred_center_of_view = child_coords
        else:
            viewport_center = self.rect.center - self.rect.bottom_left
            self.panning_vector = child_coords - viewport_center
            self._deferred_center_of_view = None


    # Properties (fold)
    panning_vector = property(get_panning_vector, set_panning_vector)


Viewport.register_event_type('on_mouse_pan')

class Grid (Widget):

    def __init__(self, rows, cols, padding=0, placement='fill'):
        super().__init__()
        self._grid = dict()
        self._num_rows = rows
        self._num_cols = cols
        self._padding = padding
        self._placement = placement

    def __iter__(self):
        yield from self._grid.values()

    def __len__(self):
        return len(self._grid)

    def __getitem__(self, index):
        return self._grid[index]

    def __setitem__(self, index, child):
        row, col = index
        self.add(row, col, child)

    def add(self, row, col, child):
        if not 0 <= row < self.num_rows:
            raise IndexError("Row out-of-bounds: row={} num_rows=0..{}".format(row, self.num_rows))
        if not 0 <= col < self.num_cols:
            raise IndexError("Column out-of-bounds: col={} num_cols=0..{}".format(col, self.num_cols))

        if (row, col) in self._grid:
            self._detach_child(self._grid[row, col])

        self._attach_child(child)
        self._grid[row, col] = child
        self._resize_and_regroup_children()

    def remove(self, row, col):
        self._detach_child(self._grid[row, col])
        del self._grid[row, col]
        self._resize_and_regroup_children()

    def do_claim(self):
        min_width = self.padding * (self.num_cols + 1)
        min_height = self.padding * (self.num_rows + 1)

        for row in range(self.num_rows):
            row_height = 0
            for col in range(self.num_cols):
                if (row, col) in self._grid:
                    child = self._grid[row, col]
                    row_height = max(child.min_height, row_height)
            min_height += row_height

        for col in range(self.num_cols):
            col_width = 0
            for row in range(self.num_rows):
                if (row, col) in self._grid:
                    child = self._grid[row, col]
                    col_width = max(child.min_width, col_width)
            min_width += col_width

        return min_width, min_height

    def do_resize_children(self):
        available_width = self.rect.width - self.padding * (self.num_cols + 1)
        available_height = self.rect.height - self.padding * (self.num_cols + 1)

        child_width = available_width / self.num_cols
        child_height = available_height / self.num_rows

        for row, col in self._grid:
            left = self.rect.left + (child_width * col) + (
                    self.padding * (col + 1))
            bottom = self.rect.bottom + (child_height * (self.num_rows - row - 1)) + (
                    self.padding * (self.num_rows - row))
            cell_rect = Rect.from_dimensions(
                    bottom=bottom, left=left,
                    width=child_width, height=child_height)

            child = self._grid[row, col]
            place_child_in_box(child, cell_rect, self.placement)

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding):
        self._padding = new_padding
        self.repack()

    padding = late_binding_property(get_padding, set_padding)

    def get_placement(self):
        return self._placement

    def set_placement(self, new_placement):
        self._placement = new_placement
        self.repack()

    placement = late_binding_property(get_placement, set_placement)

    def get_num_rows(self):
        return self._num_rows

    num_rows = late_binding_property(get_num_rows)

    def get_num_cols(self):
        return self._num_cols

    num_cols = late_binding_property(get_num_cols)

    def yield_cells(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                yield row, col


class HVBox (Widget):

    def __init__(self, padding=0, placement='fill'):
        super().__init__()
        self._children = list()
        self._expandable = set()
        self._padding = padding
        self._placement = placement

    def add(self, child, expand=False):
        self.add_back(child, expand)

    def add_front(self, child, expand=False):
        self.insert(child, 0, expand)

    def add_back(self, child, expand=False):
        self.insert(child, len(self._children), expand)

    def insert(self, child, index, expand=False):
        if expand: self._expandable.add(child)
        self._attach_child(child)
        self._children.insert(index, child)
        self._resize_and_regroup_children()

    def remove(self, child):
        self._expandable.discard(child)
        self._detach_child(child)
        self._children.remove(child)
        self._resize_and_regroup_children()

    def replace(self, index, child):
        self.remove(self._children[index])
        self.insert(child, index)

    def do_claim(self):
        raise NotImplementedError

    def do_resize_children(self, rect):
        raise NotImplementedError

    def get_children(self):
        return self._children

    children = late_binding_property(get_children)

    def get_expandable_children(self):
        return self._expandable

    expandable_children = late_binding_property(get_expandable_children)

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding):
        self._padding = new_padding
        self.repack()

    padding = late_binding_property(get_padding, set_padding)

    def get_placement(self):
        return self._placement

    def set_placement(self, new_placement):
        self._placement = new_placement
        self.repack()

    placement = late_binding_property(get_placement, set_placement)


    _dimensions = {     # (fold)
            'horizontal': ('width', 'height'),
            'vertical':   ('height', 'width'),
    }
    _coordinates = {    # (fold)
            'horizontal': ('left', 'top'),
            'vertical':   ('top', 'left'),
    }


    def _help_claim(self, orientation):
        min_width = 0
        min_height = 0
        
        # Account for children

        for child in self.children:
            child.claim()

            if orientation == 'horizontal':
                min_width += child.min_width
                min_height = max(min_height, child.min_height)
            elif orientation == 'vertical':
                min_height += child.min_height
                min_width = max(min_width, child.min_width)
            else:
                raise ValueError("Unknown orientation: {}".format(orientation))

        # Account for padding

        primary_padding = self.padding * (1 + len(self.children))
        secondary_padding = self.padding * 2

        if orientation == 'horizontal':
            min_width += primary_padding
            min_height += secondary_padding
        elif orientation == 'vertical':
            min_width += secondary_padding
            min_height += primary_padding
        else:
            raise ValueError("Unknown orientation: {}".format(orientation))

        return min_width, min_height

    def _help_resize_children(self, orientation):
        if not self.children:
            return

        dimension = self._dimensions[orientation]
        coordinate = self._coordinates[orientation]
        min_dimension = tuple('min_' + x for x in dimension)

        # Figure out how much space is available for expandable children.

        available_space = getattr(self.rect, dimension[0]) - self.padding

        for child in self.children:
            available_space -= getattr(child, min_dimension[0]) + self.padding

        # Resize each child.

        cursor, anchor = self._place_cursor(orientation)

        for child in self.children:
            box_coord_0 = cursor
            box_coord_1 = anchor
            box_dimension_0 = getattr(child, min_dimension[0])
            box_dimension_1 = getattr(self.rect, dimension[1]) - 2 * self.padding

            if child in self.expandable_children:
                box_dimension_0 += available_space / len(self.expandable_children)

            cursor = self._update_cursor(cursor, box_dimension_0, orientation)

            box_rect = Rect(0, 0, 0, 0)
            setattr(box_rect, dimension[0], box_dimension_0)
            setattr(box_rect, dimension[1], box_dimension_1)
            setattr(box_rect, coordinate[0], box_coord_0)
            setattr(box_rect, coordinate[1], box_coord_1)

            place_child_in_box(child, box_rect, self.placement)

    def _place_cursor(self, orientation):
        top = self.rect.top - self.padding
        left = self.rect.left + self.padding

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

    def do_claim(self):
        return super()._help_claim('horizontal')

    def do_resize_children(self):
        super()._help_resize_children('horizontal')


class VBox (HVBox):

    def do_claim(self):
        return super()._help_claim('vertical')

    def do_resize_children(self):
        super()._help_resize_children('vertical')


class Stack (Widget):
    """
    Have any number of children, claim enough space for the biggest one, and 
    just draw them all in the order they were added.
    """

    def __init__(self, padding=0, placement='fill'):
        super().__init__()
        self._layers = []
        self._padding = padding
        self._custom_placements = {}
        self._default_placement = placement

    def add(self, child, placement=None):
        self.add_back(child, placement)

    def add_front(self, child, placement=None):
        self.insert(child, 0, placement)

    def add_back(self, child, placement=None):
        self.insert(child, len(self.layers), placement)

    def insert(self, child, index, placement=None):
        self._attach_child(child)
        self._layers.insert(index, child)
        if placement is not None:
            self._custom_placements[child] = placement
        self._resize_and_regroup_children()

    def replace(self, index, child):
        old_child = self._layers[index]
        old_placement = self._custom_placements.get(old_child)
        self.remove(old_child)
        self.insert(child, index, old_placement)

    def remove(self, child):
        self._detach_child(child)
        self._layers.remove(child)
        self._custom_placements.pop(child, None)
        self._resize_and_regroup_children()

    def clear(self):
        for child in self.layers:
            self._detach_child(child)
        self._layers = []
        self._custom_placements = {}
        self._resize_and_regroup_children()

    def do_claim(self):
        max_child_width = 0
        max_child_height = 0

        for child in self.layers:
            max_child_width = max(max_child_height, child.min_width)
            max_child_height = max(max_child_height, child.min_height)

        min_width = max_child_width + 2 * self.padding
        min_height = max_child_height + 2 * self.padding

        return min_width, min_height

    def do_resize_children(self):
        for child in self.layers:
            place_child_in_box(
                    child,
                    self.rect.get_shrunk(self.padding),
                    self._custom_placements.get(child, self._default_placement))

    def do_regroup_children(self):
        for i, child in enumerate(self.layers):
            child.regroup(pyglet.graphics.OrderedGroup(i, self.group))

    def get_layers(self):
        return self._layers

    layers = late_binding_property(get_layers)

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding):
        self._padding = new_padding
        self.repack()

    padding = late_binding_property(get_padding, set_padding)

    def get_placement(self):
        return self._default_placement

    def set_placement(self, new_placement):
        self._default_placement = new_placement
        self.repack()

    placement = late_binding_property(get_placement, set_placement)
