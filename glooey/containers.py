#!/usr/bin/env python3

""" 
Widgets whose primary role is to contain other widgets.  Most of these widgets 
don't draw anything themselves, they just position children widgets.
"""

import pyglet
import autoprop
import vecrec

from vecrec import Vector, Rect
from collections import defaultdict
from glooey import drawing
from glooey.widget import Widget
from glooey.helpers import *

@autoprop
class Bin(Widget):

    def __init__(self):
        super().__init__()
        self._child = None

    def add(self, child):
        if self._child is not None:
            self._detach_child(self._child)

        self._child = self._attach_child(child)
        assert len(self) == 1
        self._repack_and_regroup_children()

    def clear(self):
        if self._child is not None:
            self._detach_child(self._child)
        self._child = None
        assert len(self) == 0
        self._repack_and_regroup_children()

    def do_claim(self):
        if self.child is not None:
            return self.child.claimed_size
        else:
            return 0, 0

    def do_resize_children(self):
        if self.child is not None:
            self.child._resize(self.rect)

    def get_child(self):
        return self._child


@autoprop
class Frame(Widget):
    Box = Bin
    Foreground = None
    Decoration = None
    custom_alignment = 'center'
    custom_box_layer = 2
    custom_decoration_layer = 1
    custom_autoadd_foreground = True

    def __init__(self):
        from glooey.images import Background
        super().__init__()

        self.__box = self.Box()
        self.__decoration = first_not_none((self.Decoration, Background))()

        self._attach_child(self.__box)
        self._attach_child(self.__decoration)

        if self.Foreground and self.custom_autoadd_foreground:
            self.add(self.Foreground())

    def add(self, widget):
        self.box.add(widget)

    def clear(self):
        self.box.clear()

    def do_claim(self):
        return claim_stacked_widgets(self.box, self.decoration)

    def do_regroup_children(self):
        self.box._regroup(pyglet.graphics.OrderedGroup(
            self.custom_box_layer, self.group))
        self.decoration._regroup(pyglet.graphics.OrderedGroup(
            self.custom_decoration_layer, self.group))

    def get_box(self):
        return self.__box

    def get_foreground(self):
        return self.__box.child

    def get_decoration(self):
        return self.__decoration


@autoprop
class Grid(Widget):
    custom_num_rows = 0
    custom_num_cols = 0
    custom_cell_padding = None
    custom_cell_alignment = 'fill'
    custom_default_row_height = 'expand'
    custom_default_col_width = 'expand'

    def __init__(self, num_rows=None, num_cols=None, default_row_height=None, 
            default_col_width=None):

        super().__init__()
        self._children = {}
        self._children_can_overlap = False
        self._grid = drawing.Grid(
                num_rows=num_rows or self.custom_num_rows,
                num_cols=num_cols or self.custom_num_cols,
        )
        self.cell_padding = first_not_none((
                self.custom_cell_padding, self.custom_padding, 0))
        self.cell_alignment = self.custom_cell_alignment
        self.default_row_height = first_not_none((
                default_row_height, self.custom_default_row_height))
        self.default_col_width = first_not_none((
                default_col_width, self.custom_default_col_width))

    def __getitem__(self, row_col):
        return self._children[row_col]

    def __setitem__(self, row_col, child):
        row, col = row_col
        self.add(row, col, child)

    def add(self, row, col, child):
        if (row, col) in self._children:
            self._detach_child(self._children[row, col])

        self._attach_child(child)
        self._children[row, col] = child
        self._repack_and_regroup_children()

    def remove(self, row, col):
        child = self._children[row, col]
        self._detach_child(child)
        del self._children[row, col]
        self._repack_and_regroup_children()

    def clear(self):
        for child in self._children.values():
            self._detach_child(child)
        self._children = {}
        self._repack_and_regroup_children()

    def do_claim(self):
        min_cell_rects = {
                row_col: child.claimed_rect
                for row_col, child in self._children.items()
        }
        return self._grid.make_claim(min_cell_rects)

    def do_resize_children(self):
        cell_rects = self._grid.make_cells(self.rect)
        for ij in self._children:
            align_widget_in_box(
                    self._children[ij],
                    cell_rects[ij],
                    self.cell_alignment)

    def do_find_children_near_mouse(self, x, y):
        cell = self._grid.find_cell_under_mouse(x, y)
        child = self._children.get(cell)

        if cell is None: return
        if child is None: return

        yield child

    def get_num_rows(self):
        return self._grid.num_rows

    def set_num_rows(self, new_num):
        self._grid.num_rows = new_num
        self._repack()

    def get_num_cols(self):
        return self._grid.num_cols

    def set_num_cols(self, new_num):
        self._grid.num_cols = new_num
        self._repack()

    def get_cell_indices(self):
        return [(i,j) for i in range(self.num_rows)
                      for j in range(self.num_cols)]

    def get_padding(self):
        return super().get_padding() + (self.cell_padding,)

    def set_padding(self, all=None, *, horz=None, vert=None,
            left=None, right=None, top=None, bottom=None, cell=None):
        super().set_padding(
                all=all, horz=horz, vert=vert, left=left, right=right,
                top=top, bottom=bottom)
        self._grid.inner_padding = first_not_none((cell, all, 0))
        self._repack()

    def get_cell_padding(self):
        return self._grid.inner_padding

    def set_cell_padding(self, new_padding):
        self._grid.inner_padding = new_padding
        self._repack()

    def get_cell_alignment(self):
        return self._cell_alignment

    def set_cell_alignment(self, new_alignment):
        self._cell_alignment = new_alignment
        self._repack()

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
        self._repack()

    def del_row_height(self, row):
        """
        Unset the height of the specified row.  The default height will be 
        used for that row instead.
        """
        self._grid.del_row_height(row)
        self._repack()

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
        self._repack()

    def del_col_width(self, col):
        """
        Unset the width of the specified column.  The default width will be 
        used for that column instead.
        """
        self._grid.del_col_width(col)
        self._repack()

    def get_default_row_height(self):
        return self._grid.default_row_height

    def set_default_row_height(self, new_height):
        """
        Set the default row height.  This height will be used for any rows 
        that haven't been given a specific height.  The meaning of the height 
        is the same as for set_row_height().
        """
        self._grid.default_row_height = new_height
        self._repack()

    def get_default_col_width(self):
        return self._grid.default_col_width

    def set_default_col_width(self, new_width):
        """
        Set the default column width.  This width will be used for any columns 
        that haven't been given a specific width.  The meaning of the width is 
        the same as for set_col_width().
        """
        self._grid.default_col_width = new_width
        self._repack()


@autoprop
class HVBox(Widget):
    custom_cell_padding = None
    custom_cell_alignment = 'fill'
    custom_default_cell_size = 'expand'

    def __init__(self, default_cell_size=None):
        super().__init__()
        self._children = []
        self._children_can_overlap = False
        self._sizes = {}
        self._grid = drawing.Grid()

        self.cell_padding = first_not_none((
                self.custom_cell_padding, self.custom_padding, 0))
        self.cell_alignment = self.custom_cell_alignment
        self.default_cell_size = first_not_none((
                default_cell_size, self.custom_default_cell_size))

    def add(self, widget, size=None):
        self.add_back(widget, size)

    def add_front(self, widget, size=None):
        self.insert(widget, 0, size)

    def add_back(self, widget, size=None):
        self.insert(widget, len(self._children), size)

    def pack(self, widget):
        self.add(widget, size=0)

    def pack_front(self, widget):
        self.add_front(widget, size=0)

    def pack_back(self, widget):
        self.add_back(widget, size=0)

    def insert(self, widget, index, size=None):
        self._attach_child(widget)
        self._children.insert(index, widget)
        self._sizes[widget] = size
        self._repack_and_regroup_children()

    def replace(self, old_widget, new_widget):
        old_index = self._children.index(old_widget)
        old_size = self._sizes[old_widget]
        with self.hold_updates():
            self.remove(old_widget)
            self.insert(new_widget, old_index, old_size)

    def remove(self, widget):
        self._detach_child(widget)
        self._children.remove(widget)
        del self._sizes[widget]
        self._repack_and_regroup_children()

    def clear(self):
        for child in self._children:
            self._detach_child(child)
        self._children = []
        self._sizes = {}
        self._repack_and_regroup_children()

    def do_claim(self):
        self.do_set_row_col_sizes({
                i: self._sizes[child]
                for i, child in enumerate(self._children)
                if self._sizes[child] is not None
        })
        min_cell_rects = {
                self.do_get_row_col(i): child.claimed_rect
                for i, child in enumerate(self._children)
        }
        return self._grid.make_claim(min_cell_rects)

    def do_resize_children(self):
        cell_rects = self._grid.make_cells(self.rect)
        for i, child in enumerate(self._children):
            box = cell_rects[self.do_get_row_col(i)]
            align_widget_in_box(child, box, self.cell_alignment)

    def do_find_children_near_mouse(self, x, y):
        cell = self._grid.find_cell_under_mouse(x, y)
        if cell is None: return

        child = self._children[self.do_get_index(*cell)]
        if child is None: return

        yield child

    def do_get_index(self, row, col):
        raise NotImplementedError

    def do_get_row_col(self, index):
        raise NotImplementedError

    def do_set_row_col_sizes(self, sizes):
        raise NotImplementedError

    def get_children(self):
        # Return a tuple so the list of children won't be mutable, and so the 
        # caller can't somehow inadvertently change the list of children held 
        # by the HVBox.
        return tuple(self._children)

    def get_padding(self):
        return super().get_padding() + (self.cell_padding,)

    def set_padding(self, all=None, *, horz=None, vert=None,
            left=None, right=None, top=None, bottom=None, cell=None):
        super().set_padding(
                all=all, horz=horz, vert=vert, left=left, right=right,
                top=top, bottom=bottom)
        self._grid.inner_padding = first_not_none((cell, all, 0))
        self._repack()

    def get_cell_padding(self):
        return self._grid.inner_padding

    def set_cell_padding(self, new_padding):
        self._grid.inner_padding = new_padding
        self._repack()

    def get_cell_alignment(self):
        return self._cell_alignment

    def set_cell_alignment(self, new_alignment):
        self._cell_alignment = new_alignment
        self._repack()

    def get_default_cell_size(self):
        raise NotImplementedError

    def set_default_cell_size(self, size):
        raise NotImplementedError


@autoprop
class HBox(HVBox):
    add_left = HVBox.add_front
    add_right = HVBox.add_back

    def do_get_index(self, row, col):
        return col

    def do_get_row_col(self, index):
        return 0, index

    def do_set_row_col_sizes(self, sizes):
        self._grid.col_widths = sizes

    def get_default_cell_size(self):
        return self._grid.default_col_width

    def set_default_cell_size(self, size):
        self._grid.default_col_width = size


@autoprop
class VBox(HVBox):
    add_top = HVBox.add_front
    add_bottom = HVBox.add_back

    def do_get_index(self, row, col):
        return row

    def do_get_row_col(self, index):
        return index, 0

    def do_set_row_col_sizes(self, sizes):
        self._grid.row_heights = sizes

    def get_default_cell_size(self):
        return self._grid.default_row_height

    def set_default_cell_size(self, size):
        self._grid.default_row_height = size


@autoprop
class Stack(Widget):
    """
    Have any number of children, claim enough space for the biggest one, and 
    just draw them all in layers.
    """
    custom_one_child_gets_mouse = False

    def __init__(self):
        Widget.__init__(self)
        self._children = {} # {child: layer}
        self.one_child_gets_mouse = self.custom_one_child_gets_mouse

    def add(self, widget):
        self.add_front(widget)

    def add_front(self, widget):
        layer = max(self.layers) + 1 if self.layers else 0
        self.insert(widget, layer)

    def add_back(self, widget):
        layer = min(self.layers) - 1 if self.layers else 0
        self.insert(widget, layer)

    def insert(self, widget, layer):
        self._attach_child(widget)
        self._children[widget] = layer
        self._repack_and_regroup_children()

    def remove(self, widget):
        self._detach_child(widget)
        del self._children[widget]
        self._repack_and_regroup_children()

    def clear(self):
        for child in self.children:
            self._detach_child(child)
        self._children = {}
        self._repack_and_regroup_children()

    def do_claim(self):
        return claim_stacked_widgets(*self.children)

    def do_resize_children(self):
        for child in self.children:
            align_widget_in_box(child, self.rect)

    def do_regroup_children(self):
        # If there's only one child, don't bother making an ordered group.  As 
        # I understand it, it's best to use as few groups as possible because 
        # forcing OpenGL to change states is inefficient.

        if len(self) == 1:
            child = next(iter(self.children))
            child._regroup(self.group)
        else:
            for child, layer in self._children.items():
                child._regroup(pyglet.graphics.OrderedGroup(layer, self.group))

    def do_find_children_near_mouse(self, x, y):
        for child in self.children:
            if child.is_visible and child.is_under_mouse(x, y):
                yield child
                if self.one_child_gets_mouse:
                    return

    def get_children(self):
        """
        Return a list of the children making up this stack.  The list is sorted 
        such that the widgets in the foreground come first.
        """
        # Cast to a tuple so that basic indexing operations are supported and 
        # so that the list is immutable.
        return sorted(self._children.keys(),
                key=lambda x: self._children[x], reverse=True)

    def get_layers(self):
        return sorted(self._children.values(), reverse=True)


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

    def __getitem__(self, state):
        return self._states[state]

    def __setitem__(self, state, widget):
        return self.add_state(state, widget)

    def do_claim(self):
        # Claim enough space for the biggest child, so that we won't need to 
        # repack when we change states.  (Also, I can't think of any reason why 
        # you'd want states of different sizes.)
        return claim_stacked_widgets(*self._states.values())

    def add_state(self, state, widget):
        self._remove_state(state)
        self._add_state(state, widget)
        self._repack_and_regroup_children()

    def add_states(self, **states):
        for state, widget in states.items():
            self._remove_state(state)
            self._add_state(state, widget)
        self._repack_and_regroup_children()

    def add_states_if(self, predicate, **states):
        filtered_states = {
                k: w for k,w in states.items()
                if predicate(w)
        }
        self.add_states(**filtered_states)

    def reset_states(self, **states):
        for state in list(self.known_states):
            self._remove_state(state)
        for state, widget in states.items():
            self._add_state(state, widget)
        self._repack_and_regroup_children()

    def reset_states_if(self, predicate, **states):
        filtered_states = {
                k: w for k,w in states.items()
                if predicate(w)
        }
        self.reset_states(**filtered_states)

    def remove_state(self, state):
        self.remove_states(state)

    def remove_states(self, *states):
        for state in states:
            self._remove_state(state)
        self._repack_and_regroup_children()

    def clear(self):
        self.remove_states(*self.known_states)

    def _add_state(self, state, widget):
        widget.unhide() if state == self.state else widget.hide()
        self._states[state] = widget
        self._attach_child(widget)

    def _remove_state(self, state):
        if state in self._states:
            self._detach_child(self._states[state])
            # Unhide the child so it'll show up if the user tries to reattach 
            # it somewhere else.
            self._states[state].unhide(draw=False)
            del self._states[state]

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

    def set_state_if_known(self, new_state):
        if new_state in self.known_states:
            self.state = new_state

    def get_widget(self, state):
        return self[state]

    def get_previous_state(self):
        return self._previous_state

    def get_known_states(self):
        return self._states.keys()


@autoprop
class Board(Widget):

    def __init__(self):
        super().__init__()
        self._pins = {}

    def add(self, widget, **kwargs):
        # Make the pin could fail, so do it before attaching the child.
        pin = self._make_pin(kwargs)
        # Attaching the child could also fail, so do it before updating the 
        # widget to the _pins data structure.
        self._attach_child(widget)
        self._pins[widget] = pin
        self._repack_and_regroup_children()

    def move(self, widget, **kwargs):
        self._pins[widget] = self._make_pin(kwargs)
        self._repack_and_regroup_children()

    def remove(self, widget):
        self._detach_child(widget)
        del self._pins[widget]

    def clear(self):
        for child, pin in self._pins.items():
            self._detach_child(child)
        self._pins = {}
        self._repack_and_regroup_children()

    def do_claim(self):
        min_width = 0
        min_height = 0

        for child, pin in self._pins.items():
            min_child_width = self._find_min_child_size('width', child, pin)
            min_child_height = self._find_min_child_size('height', child, pin)

            min_width = max(min_width, min_child_width)
            min_height = max(min_height, min_child_height)

        return min_width, min_height

    def do_resize_children(self):
        for child, pin in self._pins.items():
            rect = Rect.null()

            if 'width' in pin:
                rect.width = pin['width']
            if 'width_percent' in pin:
                rect.width = self.rect.width * pin['width_percent']

            if 'height' in pin:
                rect.height = pin['height']
            if 'height_percent' in pin:
                rect.height = self.rect.height * pin['height_percent']

            rect.width = max(rect.width, child.claimed_width)
            rect.height = max(rect.height, child.claimed_height)

            if 'left' in pin:
                rect.left = pin['left']
            if 'left_percent' in pin:
                rect.left = self.rect.width * pin['left_percent']

            if 'right' in pin:
                rect.right = pin['right']
            if 'right_percent' in pin:
                rect.right = self.rect.width * pin['right_percent']

            if 'center_x' in pin:
                rect.center_x = pin['center_x']
            if 'center_x_percent' in pin:
                rect.center_x = self.rect.width * pin['center_x_percent']

            if 'top' in pin:
                rect.top = pin['top']
            if 'top_percent' in pin:
                rect.top = self.rect.height * pin['top_percent']

            if 'bottom' in pin:
                rect.bottom = pin['bottom']
            if 'bottom_percent' in pin:
                rect.bottom = self.rect.height * pin['bottom_percent']

            if 'center_y' in pin:
                rect.center_y = pin['center_y']
            if 'center_y_percent' in pin:
                rect.center_y = self.rect.height * pin['center_y_percent']

            rect.left += self.rect.left
            rect.bottom += self.rect.bottom

            child._resize(rect)

    def do_regroup_children(self):
        for child, pin in self._pins.items():
            if 'layer' in pin:
                group = pyglet.graphics.OrderedGroup(pin['layer'], self.group)
            else:
                group = self.group

            child._regroup(group)

    def _make_pin(self, kwargs):

        # Put the argument in a data structure that will keep track of which 
        # keys have been used, so we can give a nice error if we find an 
        # unexpected (i.e. misspelled) argument.

        class argdict(dict): #

            def __init__(self, kwargs): #
                self.update(kwargs)
                self.unused_keys = set(kwargs.keys())

            def __getitem__(self, key): #
                self.unused_keys.discard(key)
                return super().__getitem__(key)

        kwargs = argdict(kwargs)

        # Check to make sure the position of the widget isn't over- or 
        # under-specified.

        all_x_args = [
                'rect',
                'left', 'left_percent',
                'center_x', 'center_x_percent',
                'right', 'right_percent',
                'top_left', 'top_left_percent',
                'top_center', 'top_center_percent',
                'top_right', 'top_right_percent',
                'center_left', 'center_left_percent',
                'center', 'center_percent',
                'center_right', 'center_right_percent',
                'bottom_left', 'bottom_left_percent',
                'bottom_center', 'bottom_center_percent',
                'bottom_right', 'bottom_right_percent',
        ]
        all_y_args = [
                'rect',
                'top', 'top_percent',
                'center_y', 'center_y_percent',
                'bottom', 'bottom_percent',
                'top_left', 'top_left_percent',
                'top_center', 'top_center_percent',
                'top_right', 'top_right_percent',
                'center_left', 'center_left_percent',
                'center', 'center_percent',
                'center_right', 'center_right_percent',
                'bottom_left', 'bottom_left_percent',
                'bottom_center', 'bottom_center_percent',
                'bottom_right', 'bottom_right_percent',
        ]
        all_w_args = [
                'rect',
                'width', 'width_percent',
        ]
        all_h_args = [
                'rect',
                'height', 'height_percent',
        ]

        x_args = {x for x in all_x_args if x in kwargs}
        y_args = {y for y in all_y_args if y in kwargs}
        w_args = {w for w in all_w_args if w in kwargs}
        h_args = {h for h in all_h_args if h in kwargs}

        if len(x_args) > 1:
            raise UsageError(f"multiple x positions specified: {''.join(sorted(x_args))}")
        if len(x_args) < 1:
            raise UsageError(f"no x position specified, only: {', '.join(kwargs.keys())}")

        if len(y_args) > 1:
            raise UsageError(f"multiple y positions specified: {''.join(sorted(y_args))}")
        if len(y_args) < 1:
            raise UsageError(f"no y position specified, only: {', '.join(kwargs.keys())}")

        if len(w_args) > 1:
            raise UsageError(f"multiple widths specified: {''.join(sorted(w_args))}")
        if len(h_args) > 1:
            raise UsageError(f"multiple heights specified: {''.join(sorted(h_args))}")

        # Create the pin (which is just a dictionary) and fill it in with any 
        # parameters that can be copied directly from the argument list.

        pin_keys = [
                'left', 'left_percent',
                'center_x', 'center_x_percent',
                'right', 'right_percent',
                'top', 'top_percent',
                'center_y', 'center_y_percent',
                'bottom', 'bottom_percent',
                'width', 'width_percent',
                'height', 'height_percent',
                'layer',
        ]
        pin = {
                k: kwargs[k] for k in pin_keys 
                if k in kwargs
        }

        # If a rectangle was provided in the argument list, using it to fill in 
        # the pin.

        if 'rect' in kwargs:
            rect = kwargs['rect']
            pin['left'] = rect.left
            pin['bottom'] = rect.bottom
            pin['width'] = rect.width
            pin['height'] = rect.height

        # If any corners or edges were specified in the argument list (e.g.  
        # top_left, bottom_right, center, etc.), use them to fill in the pin.

        vector_keys = {
                'top_left':      ('left',     'top'),
                'top_center':    ('center_x', 'top'),
                'top_right':     ('right',    'top'),
                'center_left':   ('left',     'center_y'),
                'center':        ('center_x', 'center_y'),
                'center_right':  ('right',    'center_y'),
                'bottom_left':   ('left',     'bottom'),
                'bottom_center': ('center_x', 'bottom'),
                'bottom_right':  ('right',    'bottom'),
                'top_left_percent':      ('left_percent',     'top_percent'),
                'top_center_percent':    ('center_x_percent', 'top_percent'),
                'top_right_percent':     ('right_percent',    'top_percent'),
                'center_left_percent':   ('left_percent',     'center_y_percent'),
                'center_percent':        ('center_x_percent', 'center_y_percent'),
                'center_right_percent':  ('right_percent',    'center_y_percent'),
                'bottom_left_percent':   ('left_percent',     'bottom_percent'),
                'bottom_center_percent': ('center_x_percent', 'bottom_percent'),
                'bottom_right_percent':  ('right_percent',    'bottom_percent'),
        }

        for key in vector_keys:
            if key in kwargs:
                x, y = vecrec.cast_anything_to_vector(kwargs[key])
                kx, ky = vector_keys[key]
                pin[kx] = x
                pin[ky] = y

        # Make sure the pin has both a width and a height.

        if 'width' not in pin and 'width_percent' not in pin:
            pin['width'] = 0
        if 'height' not in pin and 'height_percent' not in pin:
            pin['height'] = 0

        # Make sure all the arguments were used.

        if kwargs.unused_keys:
            raise UsageError(f"got unexpected keyword argument(s): {', '.join(kwargs.unused_keys)}")

        # Make sure none of the parameters in the pin are totally impossible.  
        # These checks obviate the need for a number of divide-by-zero checks 
        # in do_claim() and do_resize_children().

        def sanity_check(pin, field, *bounds): #
            if field in pin:
                if pin[field] in bounds:
                    raise UsageError(f"{field} cannot be {pin[field]}")
                if pin[field] < 0 or pin[field] > 1:
                    raise UsageError(f"{field} must be between 0 and 1, not {pin[field]}")

        sanity_check(pin, 'left_percent', 1)
        sanity_check(pin, 'right_percent', 0)
        sanity_check(pin, 'center_x_percent', 0, 1)
        sanity_check(pin, 'bottom_percent', 1)
        sanity_check(pin, 'top_percent', 0)
        sanity_check(pin, 'center_y_percent', 0, 1)
        sanity_check(pin, 'width_percent', 0)
        sanity_check(pin, 'height_percent', 0)

        return pin

    def _find_min_child_size(self, dimension, child, pin):
        # Initially set the board size to a negative number.  If it's still 
        # negative by the end of the function, that means none of the 
        # conditions triggered and there's a bug in the code.

        board_size = -1

        # Decide which dimension to look at.  The logic is the same for 
        # determining the width and height claims, but the attributes differ.

        if dimension == 'width':
            child_claim = child.claimed_width
            dimension_percent = 'width_percent'
            near, near_percent = 'left', 'left_percent'
            mid, mid_percent = 'center_x', 'center_x_percent'
            far, far_percent = 'right', 'right_percent'
        elif dimension == 'height':
            child_claim = child.claimed_height
            dimension_percent = 'height_percent'
            near, near_percent = 'bottom', 'bottom_percent'
            mid, mid_percent = 'center_y', 'center_y_percent'
            far, far_percent = 'top', 'top_percent'
        else:
            raise AssertionError(f"unknown dimension: {dimension}")

        # Find the claim if an absolute size was given.

        if dimension in pin:
            child_size = max(child_claim, pin[dimension])
        
            if near in pin:
                board_size = pin[near] + child_size

            if far in pin:
                if pin[far] < child_size:
                    raise UsageError(f"cannot fit {child}: {dimension}={child_size} px; {far}={pin[far]} px")
                board_size = pin[far]

            if mid in pin:
                if pin[mid] < child_size / 2:
                    raise UsageError(f"cannot fit {child}: {dimension}={child_size} px; {mid}={pin[mid]} px")
                board_size = pin[mid] + child_size / 2

            if near_percent in pin:
                board_size = child_size / (1 - pin[near_percent])

            if far_percent in pin:
                board_size = child_size / pin[far_percent]

            if mid_percent in pin:
                board_size = max(
                        (child_size / 2) / (1 - pin[mid_percent]),
                        (child_size / 2) / (pin[mid_percent]))

        # Find the claim if the size was given as a percentage of the whole 
        # board.

        if dimension_percent in pin:
            child_size = child_claim
            size_percent = pin[dimension_percent]

            if near in pin:
                board_size = max(
                        pin[near] + child_size,
                        # Explicitly check for zero so that near=0; size_percent=1 is allowed.
                        0 if pin[near] == 0 else pin[near] / (1 - size_percent),
                        child_size / size_percent)

            if far in pin:
                if pin[far] < child_size:
                    raise UsageError(f"cannot fit {child}: {dimension}={child_size} px; {dimension_percent}={size_percent}; {far}={pin[far]} px")
                board_size = max(
                        pin[far],
                        child_size / size_percent)

            if mid in pin:
                if pin[mid] < child_size / 2:
                    raise UsageError(f"cannot fit {child}: {dimension}={child_size} px; {mid}={pin[mid]} px")
                board_size = max(
                        pin[mid] + child_size / 2,
                        pin[mid] / (1 - size_percent / 2),
                        child_size / size_percent)

            if near_percent in pin:
                if pin[near_percent] + size_percent > 1:
                    raise UsageError(f"cannot fit {child}: {near_percent}={pin[near_percent]}; {dimension_percent}={size_percent}")
                board_size = child_size / size_percent

            if far_percent in pin:
                if pin[far_percent] < size_percent:
                    raise UsageError(f"cannot fit {child}: {far_percent}={pin[far_percent]}; {dimension_percent}={size_percent}")
                board_size = child_size / size_percent

            if mid_percent in pin:
                if pin[mid_percent] + size_percent / 2 > 1 or pin[mid_percent] < size_percent / 2:
                    raise UsageError(f"cannot fit {child}: {mid_percent}={pin[mid_percent]}; {dimension_percent}={size_percent}")
                board_size = child_size / size_percent

        assert board_size > -1
        return board_size



def align_widget_in_box(widget, box_rect, alignment='fill', widget_rect=None):
    if widget_rect is None:
        widget_rect = widget.claimed_rect
    drawing.align(alignment, widget_rect, box_rect)
    widget._resize(widget_rect)

def claim_stacked_widgets(*widgets):
    max_widget_width = 0
    max_widget_height = 0

    for widget in widgets:
        max_widget_width = max(max_widget_width, widget.claimed_width)
        max_widget_height = max(max_widget_height, widget.claimed_height)

    return max_widget_width, max_widget_height


