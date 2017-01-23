""" 
Widgets whose primary role is to contain other widgets.  Most of these widgets 
don't draw anything themselves, they just position children widgets.
"""

import pyglet
import vecrec
import autoprop

from vecrec import Vector, Rect
from collections import defaultdict
from pprint import pprint
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

def cast_to_placement_function(key_or_function):
    try:
        return placement_functions[key_or_function]
    except KeyError:
        return key_or_function

def place_widget_in_box(widget, box_rect, key_or_function, widget_rect=None):
    placement_function = cast_to_placement_function(key_or_function)

    if widget_rect is None:
        widget_rect = widget.min_rect

    placement_function(widget_rect, box_rect)
    widget.resize(widget_rect)


@autoprop
class BinMixin:
    """
    Provide add() and clear() methods for containers that can only have one 
    child widget at a time.  The add() method will automatically remove the 
    existing child if necessary.

    This mixin is intended for classes that are like Bins in the sense that 
    they can only have one child, but don't want to inherit the rest of the 
    actual Bin class's interface, namely support for padding and custom child 
    placement.
    """

    def __init__(self):
        self._child = None

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


@autoprop
class PaddingMixin:

    def __init__(self, padding=0):
        self._padding = padding

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding, repack=True):
        if new_padding is not None:
            self._padding = new_padding
            if repack: self.repack()


@autoprop
class PlacementMixin:

    def __init__(self, placement='fill'):
        self._default_placement = placement
        self._custom_placements = {}

    def get_placement(self):
        return self._default_placement

    def set_placement(self, new_placement):
        self._default_placement = new_placement
        self.repack()

    def _get_placement(self, key):
        return self._custom_placements.get(key, self._default_placement)

    def _get_custom_placement(self, key):
        return self._custom_placements.get(key)

    def _set_custom_placement(self, key, new_placement, repack=True):
        if new_placement is not None:
            self._custom_placements[key] = new_placement
            if repack: self.repack()

    def _unset_custom_placement(self, key, repack=True):
        if key in self._custom_placements:
            del self._custom_placements[key]
            if repack: self.repack()



@autoprop
class Bin (Widget, BinMixin, PaddingMixin, PlacementMixin):

    def __init__(self, padding=0, placement='fill'):
        Widget.__init__(self)
        BinMixin.__init__(self)
        PaddingMixin.__init__(self, padding)
        PlacementMixin.__init__(self, placement)

    def add(self, child, placement=None, padding=None):
        self._set_custom_placement(child, placement, repack=False)
        self.set_padding(padding, repack=False)
        BinMixin.add(self, child)

    def clear(self):
        self._unset_custom_placement(child, placement, repack=False)
        BinMixin.clear(self)

    def do_claim(self):
        min_width = 2 * self.padding
        min_height = 2 * self.padding

        if self.child is not None:
            min_width += self.child.min_width
            min_height += self.child.min_height

        return min_width, min_height

    def do_resize_children(self):
        if self.child is not None:
            place_widget_in_box(
                    self.child,
                    self.rect.get_shrunk(self.padding),
                    self._get_placement(self.child))


@autoprop
class Viewport (Widget, BinMixin):

    class PanningGroup (pyglet.graphics.Group):

        def __init__(self, viewport, parent=None):
            pyglet.graphics.Group.__init__(self, parent)
            self.viewport = viewport

        def set_state(self):
            translation = -self.viewport.get_child_coords(0, 0)
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(translation.x, translation.y, 0)

        def unset_state(self):
            pyglet.gl.glPopMatrix()

    def __init__(self, sensitivity=3):
        Widget.__init__(self)
        BinMixin.__init__(self)

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

    def do_attach(self):
        # If this line raises a pyglet EventException, you're probably trying 
        # to attach this widget to a GUI that doesn't support mouse pan events.  
        # See the Viewport documentation for more information.
        self.root.push_handlers(self.on_mouse_pan)

    def do_detach(self):
        self.window.remove_handler(self.on_mouse_pan)

    def do_claim(self):
        # The widget being displayed in the viewport can claim however much 
        # space it wants.  The viewport doesn't claim any space, because it can 
        # be as small as it needs to be.
        return 0, 0

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


Viewport.register_event_type('on_mouse_pan')

@autoprop
class Grid (Widget, PlacementMixin):

    def __init__(self, rows=0, cols=0, padding=0, placement='fill'):
        Widget.__init__(self)
        PlacementMixin.__init__(self, placement)
        self._children = {}
        self._children_can_overlap = False
        self._grid = drawing.Grid(
                num_rows=rows,
                num_cols=cols,
                padding=padding,
        )

    def __iter__(self):
        yield from self._children.values()

    def __len__(self):
        return len(self._children)

    def __getitem__(self, row_col):
        return self._children[row_col]

    def __setitem__(self, row_col, child):
        row, col = row_col
        self.add(row, col, child)

    def add(self, row, col, child, placement=None):
        if (row, col) in self._children:
            self._detach_child(self._children[row, col])

        self._attach_child(child)
        self._children[row, col] = child
        self._set_custom_placement((row, col), placement, repack=False)
        self._resize_and_regroup_children()

    def remove(self, row, col):
        child = self._children[row, col]
        self._detach_child(child)
        del self._children[row, col]
        self._unset_custom_placement((row, col), placement, repack=False)
        self._resize_and_regroup_children()

    def do_claim(self):
        min_cell_rects = {
                row_col: child.min_rect
                for row_col, child in self._children.items()
        }
        return self._grid.make_claim(min_cell_rects)

    def do_resize_children(self):
        cell_rects = self._grid.make_cells(self.rect)
        for ij in self._children:
            child = self._children[ij]
            placement = self._get_placement(ij)
            place_widget_in_box(child, cell_rects[ij], placement)

    def get_num_rows(self):
        return self._grid.num_rows

    def set_num_rows(self, new_num):
        self._grid.num_rows = new_num
        self.repack()

    def get_num_cols(self):
        return self._grid.num_rows

    def set_num_cols(self, new_num):
        self._grid.num_cols = new_num
        self.repack()

    def get_padding(self):
        return self._grid.padding

    def set_padding(self, new_padding):
        self._grid.padding = new_padding
        self.repack()

    def get_row_height(self, row):
        return self._grid.row_heights[row]

    def set_row_height(self, row, new_height):
        """
        Set the height of the given row.  You can provide the height as an 
        integer or the string 'expand'.
        
        If you provide an integer, the row will be that many pixels tall, so 
        long as all the cells in that row fit in that space.  If the cells 
        don't fit, the row will be just tall enough to fit them.  For this 
        reason, it is common to specify a height of "0" to make the row as 
        short as possible.

        If you provide the string 'expand', the row will grow to take up any 
        extra space allocated to the grid but not used by any of the other 
        rows.  If multiple rows are set the expand, the extra space will 
        be divided evenly between them.
        """
        self._grid.set_row_height(row, new_height)
        self.repack()

    def get_col_width(self, col):
        return self._grid.col_widths[col]

    def set_col_width(self, col, new_width):
        """
        Set the width of the given column.  You can provide the width as an 
        integer or the string 'expand'.
        
        If you provide an integer, the column will be that many pixels wide, so 
        long as all the cells in that column fit in that space.  If the cells 
        don't fit, the column will be just wide enough to fit them.  For this 
        reason, it is common to specify a width of "0" to make the column as 
        narrow as possible.

        If you provide the string 'expand', the column will grow to take up any 
        extra space allocated to the grid but not used by any of the other 
        columns.  If multiple columns are set the expand, the extra space will 
        be divided evenly between them.
        """
        self._grid.set_col_width(col, new_width)
        self.repack()

    def unset_row_height(self, row):
        """
        Unset the height of the specified row.  The default height will be 
        used for that row instead.
        """
        self._grid.unset_row_height(row)
        self.repack()

    def unset_col_width(self, col):
        """
        Unset the width of the specified column.  The default width will be 
        used for that column instead.
        """
        self._grid.unset_col_width(col)
        self.repack()

    def get_default_row_height(self):
        return self._grid.default_row_height

    def set_default_row_height(self, new_height):
        """
        Set the default row height.  This height will be used for any rows 
        that haven't been given a specific height.  The meaning of the height 
        is the same as for set_row_height().
        """
        self._grid.default_row_height = new_height
        self.repack()

    def get_default_col_width(self):
        return self._grid.default_col_width

    def set_default_col_width(self, new_width):
        """
        Set the default column width.  This width will be used for any columns 
        that haven't been given a specific width.  The meaning of the width is 
        the same as for set_col_width().
        """
        self._grid.default_col_width = new_width
        self.repack()


@autoprop
class HVBox (Widget, PlacementMixin):

    def __init__(self, padding=0, placement='fill'):
        Widget.__init__(self)
        PlacementMixin.__init__(self, placement)
        self._children = []
        self._children_can_overlap = False
        self._sizes = {}
        self._grid = drawing.Grid(
                padding=padding,
        )

    def __iter__(self):
        yield from self._children

    def __len__(self):
        return len(self._children)

    def add(self, child, size=None, placement=None):
        self.add_back(child, size, placement)

    def add_front(self, child, size=None, placement=None):
        self.insert(child, 0, size, placement)

    def add_back(self, child, size=None, placement=None):
        self.insert(child, len(self._children), size, placement)

    def insert(self, child, index, size=None, placement=None):
        self._attach_child(child)
        self._children.insert(index, child)
        self._sizes[child] = size
        self._set_custom_placement(child, placement, repack=False)
        self._resize_and_regroup_children()

    def replace(self, old_child, new_child):
        old_index = self._children.index(old_child)
        old_size = self._sizes[old_child]
        old_placement = self._get_custom_placement(old_child)
        self.remove(old_child, repack=False)
        self.insert(new_child, old_index, old_size, old_placement)

    def remove(self, child, repack=True):
        self._detach_child(child)
        self._children.remove(child)
        del self._sizes[child]
        self._unset_custom_placement(child)
        if repack: self._resize_and_regroup_children()

    def do_claim(self):
        self.do_set_row_col_sizes({
                i: self._sizes[child]
                for i, child in enumerate(self._children)
                if self._sizes[child] is not None
        })
        min_cell_rects = {
                self.do_get_row_col(i): child.min_rect
                for i, child in enumerate(self._children)
        }
        return self._grid.make_claim(min_cell_rects)

    def do_resize_children(self):
        cell_rects = self._grid.make_cells(self.rect)
        for i, child in enumerate(self._children):
            box = cell_rects[self.do_get_row_col(i)]
            placement = self._get_placement(child)
            place_widget_in_box(child, box, placement)

    def do_get_row_col(self, index):
        raise NotImplementedError

    def do_set_row_col_sizes(self, sizes):
        raise NotImplementedError

    def get_children(self):
        return self._children[:]

    def get_padding(self):
        return self._grid.padding

    def set_padding(self, new_padding):
        self._grid.padding = new_padding
        self.repack()


@autoprop
class HBox (HVBox):

    add_left = HVBox.add_front
    add_right = HVBox.add_back

    def do_get_row_col(self, index):
        return 0, index

    def do_set_row_col_sizes(self, sizes):
        self._grid.col_widths = sizes

    def get_default_size(self):
        return self._grid.default_col_width

    def set_default_size(self, size):
        self._grid.default_col_width = size


@autoprop
class VBox (HVBox):

    add_top = HVBox.add_front
    add_bottom = HVBox.add_back

    def do_get_row_col(self, index):
        return index, 0

    def do_set_row_col_sizes(self, sizes):
        self._grid.row_heights = sizes

    def get_default_size(self):
        return self._grid.default_row_height

    def set_default_size(self, size):
        self._grid.default_row_height = size


@autoprop
class Stack (Widget, PaddingMixin, PlacementMixin):
    """
    Have any number of children, claim enough space for the biggest one, and 
    just draw them all in the order they were added.

    For the button, it would be more useful to specify a layer.  Stacking is 
    still a nice default, though.
    """

    def __init__(self, padding=0, placement='fill'):
        Widget.__init__(self)
        PaddingMixin.__init__(self, padding)
        PlacementMixin.__init__(self, placement)
        self._children = {} # {child: layer}

    def __iter__(self):
        yield from sorted(
                self._children.keys(),
                key=lambda x: self._children[x],
                reverse=True)

    def __len__(self):
        return len(self._children)

    def add(self, widget, placement=None):
        self.add_top(widget, placement)

    def add_top(self, widget, placement=None):
        layer = max(self.layers) + 1 if self.layers else 0
        self.insert(widget, layer, placement)

    def add_bottom(self, widget, placement=None):
        layer = min(self.layers) - 1 if self.layers else 0
        self.insert(widget, layer, placement)

    def insert(self, widget, layer, placement=None):
        self._attach_child(widget)
        self._children[widget] = layer
        self._set_custom_placement(widget, placement, repack=False)
        self._resize_and_regroup_children()

    def remove(self, widget):
        self._detach_child(widget)
        del self._children[widget]
        self._unset_custom_placement(widget, repack=False)
        self._resize_and_regroup_children()

    def clear(self):
        for child in self.children:
            self._detach_child(child)
        self._children = {}
        self._custom_placements = {}
        self._resize_and_regroup_children()

    def do_claim(self):
        max_child_width = 0
        max_child_height = 0

        for child in self.children:
            max_child_width = max(max_child_height, child.min_width)
            max_child_height = max(max_child_height, child.min_height)

        min_width = max_child_width + 2 * self.padding
        min_height = max_child_height + 2 * self.padding

        return min_width, min_height

    def do_resize_children(self):
        for child in self.children:
            place_widget_in_box(
                    child,
                    self.rect.get_shrunk(self.padding),
                    self._get_placement(child))

    def do_regroup_children(self):
        # If there's only one child, don't bother making an ordered group.  As 
        # I understand it, it's best to use as few groups as possible because 
        # forcing OpenGL to change states is inefficient.

        if len(self) == 1:
            only_child = next(iter(self.children))
            only_child.regroup(self.group)
        else:
            for child, layer in self._children.items():
                child.regroup(pyglet.graphics.OrderedGroup(layer, self.group))

    def get_children(self):
        return self._children.keys()

    def get_layers(self):
        return self._children.values()


@autoprop
class Deck(Widget):
    """
    Display one of a number of child widgets depending on the state specified 
    by the user.
    """

    def __init__(self, initial_state, **states):
        super().__init__()
        self._current_state = initial_state
        self._previous_state = initial_state
        self._states = {}
        self.add_states(**states)

    def do_claim(self):
        # Claim enough space for the biggest child, so that we won't need to 
        # repack when we change states.  (Also, I can't think of any reason why 
        # you'd want states of different sizes.)

        min_width = 0
        min_height = 0

        for child in self._states.values():
            min_width = max(child.min_width, min_width)
            min_height = max(child.min_height, min_height)

        return min_width, min_height

    def add_state(self, state, widget):
        self.add_states(**{state: widget})

    def add_states(self, **states):
        for state, widget in states.items():
            if state == self.state:
                widget.unhide()
            else:
                widget.hide()
            self._states[state] = widget
            self._attach_child(widget)

        self.repack()

    def remove_state(self, state):
        self.remove_states(state)

    def remove_states(self, *states):
        for state in states:
            self._detach_child(self._states[state])
            self._states[state].unhide()    # Unhide the child so it'll show up 
            del self._states[state]         # if the user tries to reattach it 
        self.repack()                       # somewhere else.

    def clear_states(self):
        self.remove_states(self.known_states)

    def get_state(self):
        return self._current_state

    def set_state(self, new_state):
        if new_state not in self.known_states:
            raise ValueError(f"unknown state '{new_state}'")

        self._previous_state = self._current_state
        self._current_state = new_state

        if self._current_state != self._previous_state:
            self._states[self._current_state].unhide()

            # The previous state could've been removed since the state was last 
            # changed.  In this case it will have already been hidden, so we 
            # don't need to do anything.
            try: self._states[self._previous_state].hide()
            except KeyError: pass

    def get_previous_state(self):
        return self._previous_state

    def get_known_states(self):
        return self._states.keys()


