#!/usr/bin/env python3

""" 
Widgets whose primary role is to contain other widgets.  Most of these widgets 
don't draw anything themselves, they just position children widgets.

For conventional box-like layouts, see `Grid`, 'HBox`, and `VBox`.  For more 
flexible and ad-hoc layouts, see `Board`.  For putting backgrounds and borders 
around other widgets, see `Frame`.
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
    """
    A container that can hold a single widget.

    Bins are most often used to set limits on how big another widget can be.  
    For example, you would use a Bin with some padding to keep the contents of 
    a `Frame` from getting to close to the frame's edge.  Most often, bins are 
    used as inner classes within more complicated widgets.  It's less common to 
    see them used directly.
    """

    def __init__(self):
        super().__init__()
        self._child = None

    def add(self, child):
        """
        Put a widget into the bin.

        If the bin already had a child, it is removed and replaced by the new 
        one.
        """
        if self._child is not None:
            self._detach_child(self._child)

        self._child = self._attach_child(child)
        assert len(self) == 1
        self._repack_and_regroup_children()

    def clear(self):
        """
        Empty the bin.

        It's OK to call this method if the bin is empty to begin with.
        """
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
        """
        Return the widget currently in the bin, or None if the bin is empty.
        """
        return self._child


@autoprop
class Frame(Widget):
    """
    Visually offset a widget from its surroundings.

    See the descriptions of the `Decoration`, `Box`, and `Content` inner 
    classes for information on how to control the appearance of the frame.
    """

    Box = Bin
    """
    The container that will hold the content of the frame.  Often this is 
    `Bin`, with the `custom_padding` attribute set to keep the content a 
    reasonable distance from  the edge of the frame.
    """

    Content = None
    """
    The widget that will go inside the frame.  It's more common to add this 
    widget after the frame has been created using the `add()` method, but 
    sometimes it's convenient for a subclass to automatically fill in its
    content.
    """

    Decoration = None
    """
    The widget that will appear in the background of the frame.  Often this is 
    either `Background` (for variably-sized frames) or `Image` (for fixed-size 
    frames).
    """

    custom_box_layer = 2
    """
    The z-order for the contents of the frame (i.e. the box and its children).  
    By default this is on top of the decorations.
    """

    custom_decoration_layer = 1
    """
    The z-order for the frame's decorations (i.e. the border and the 
    background).  By default these are below the content.
    """

    custom_autoadd_content = True
    """
    If a `Content` inner class is specified, automatically instantiate it and 
    add it to the frame.  This behavior in enabled by default.
    """

    custom_alignment = 'center'

    def __init__(self):
        from glooey.images import Background
        super().__init__()

        self.__box = self.Box()
        self.__decoration = first_not_none((self.Decoration, Background))()

        self._attach_child(self.__box)
        self._attach_child(self.__decoration)

        if self.Content and self.custom_autoadd_content:
            self.add(self.Content())

    def add(self, widget):
        """
        Add a widget to the frame.

        This method just calls `add()` on whatever widget the `Box` class is.  
        Normally `Box` is a `Bin`, so this makes sense.  If you replace `Box` 
        with something else, fro example `Grid`, you might want to also 
        reimplement this method.
        """
        self.box.add(widget)

    def clear(self):
        """
        Remove any widgets from the frame.
        """
        self.box.clear()

    def do_claim(self):
        return claim_stacked_widgets(self.box, self.decoration)

    def do_regroup_children(self):
        self.box._regroup(pyglet.graphics.OrderedGroup(
            self.custom_box_layer, self.group))
        self.decoration._regroup(pyglet.graphics.OrderedGroup(
            self.custom_decoration_layer, self.group))

    def get_box(self):
        """
        Return the widget holding the content of the frame.
        """
        return self.__box

    def get_content(self):
        """
        Return the widget being displayed in the frame.
        """
        return self.__box.child

    def get_decoration(self):
        """
        Return the widget appearing in the background of the frame.
        """
        return self.__decoration


@autoprop
class Grid(Widget):
    """
    Arrange widgets in a rectangular grid.

    You can add widgets to the grid using either the `add()` method or the 
    square-bracket operator (e.g. `grid[row, col] = widget`).  You don't need 
    to specify the size of the grid in advance, it will automatically create 
    enough rows and columns to fit all of its children.  The `set_row_height()` 
    and `set_col_width()` methods are useful for controlling the dimensions of 
    the grid.
    """

    custom_num_rows = 0
    """
    The minimum number of rows for the grid to have.
    """

    custom_num_cols = 0
    """
    The minimum number of columns for the grid to have.
    """

    custom_cell_padding = None
    """
    The padding between the cells of the grid.

    This is distinct from `custom_padding`, which is the padding around the 
    edge of the grid.
    """

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
        """
        Return the widget at the given position in the grid.

        If no such child exists, a KeyError will be raised.
        """
        return self._children[row_col]

    def __setitem__(self, row_col, child):
        """
        Add a widget to the grid at the given position.

        See `add()` for more details.
        """
        row, col = row_col
        self.add(row, col, child)

    def add(self, row, col, child):
        """
        Add a widget to the grid at the given position.

        It's not an error to specify a cell that's not currently in the grid 
        (i.e. 3,3 in a 2x2 grid).  The grid will simply be expanded to fit all 
        of its children.
        """
        if (row, col) in self._children:
            self._detach_child(self._children[row, col])

        self._attach_child(child)
        self._children[row, col] = child
        self._repack_and_regroup_children()

    def remove(self, row, col):
        """
        Remove the widget at the given position in the grid.

        If no such child exists, a KeyError will be raised.
        """
        child = self._children[row, col]
        self._detach_child(child)
        del self._children[row, col]
        self._repack_and_regroup_children()

    def clear(self):
        """
        Remove all widgets from the grid.

        It's ok to call this method on a grid that's already empty.
        """
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
        """
        Return the number of rows in the grid.
        """
        return self._grid.num_rows

    def set_num_rows(self, new_num):
        """
        Set the minimum number of rows for the grid.

        The grid could have more rows because it will grow to fit any cells 
        added to it.
        """
        self._grid.num_rows = new_num
        self._repack()

    def get_num_cols(self):
        """
        Return the number of columns in the grid.
        """
        return self._grid.num_cols

    def set_num_cols(self, new_num):
        """
        Set the minimum number of columns for the grid.

        The grid could have more columns because it will grow to fit any 
        cells added to it.
        """
        self._grid.num_cols = new_num
        self._repack()

    def get_cell_indices(self):
        """
        Return row and column indices for every cell in the grid.

        This includes cells that aren't necessarily associated with any widget.  
        For example, if a grid has a child in position (1,1) and none anywhere 
        else, then it has 2 rows and columns and this method would return:
        [(0,0), (0,1), (1,0), (1,1)]
        """
        return [(i,j) for i in range(self.num_rows)
                      for j in range(self.num_cols)]

    def get_padding(self):
        """
        Return the padding on all sides of this widget, plus the padding 
        between the cells, as a (left, right, top bottom, cell) tuple.
        """
        return super().get_padding() + (self.cell_padding,)

    def set_padding(self, all=None, *, horz=None, vert=None,
            left=None, right=None, top=None, bottom=None, cell=None):
        """
        Set the padding for any or all sides of this widget.
        """
        super().set_padding(
                all=all, horz=horz, vert=vert, left=left, right=right,
                top=top, bottom=bottom)
        self._grid.inner_padding = first_not_none((cell, all, 0))
        self._repack()

    def get_cell_padding(self):
        """
        Return the padding between the cells of this widget.
        """
        return self._grid.inner_padding

    def set_cell_padding(self, new_padding):
        """
        Set the padding between the cells of this widget.
        """
        self._grid.inner_padding = new_padding
        self._repack()

    def get_cell_alignment(self):
        """
        Return how widgets are aligned within their cells.
        """
        return self._cell_alignment

    def set_cell_alignment(self, new_alignment):
        """
        Specify how widgets should be aligned within their cells.
        """
        self._cell_alignment = new_alignment
        self._repack()

    def get_row_height(self, row):
        """
        Return the height of the given row.
        """
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
        """
        Return the width of the given column.
        """
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
        """
        Get the default row height.
        """
        return self._grid.default_row_height

    def set_default_row_height(self, new_height):
        """
        Set the default row height.
        
        This height will be used for any rows that haven't been given a 
        specific height.  The meaning of the height is the same as for 
        `set_row_height()`.
        """
        self._grid.default_row_height = new_height
        self._repack()

    def get_default_col_width(self):
        """
        Get the default column width.
        """
        return self._grid.default_col_width

    def set_default_col_width(self, new_width):
        """
        Set the default column width.
        
        This width will be used for any columns that haven't been given a 
        specific width.  The meaning of the width is the same as for 
        `set_col_width()`.
        """
        self._grid.default_col_width = new_width
        self._repack()


@autoprop
class HVBox(Widget):
    """
    An abstract base class for containers that can pack widgets into either a 
    single row or single column.

    The two main `HVBox` subclasses are `HBox` and `VBox`.  The `add()` and 
    `pack()` methods are the most convenient ways to add widgets to these 
    containers.  You can decide how much space you want to allocate to each 
    widget you add: e.g. as little space as possible, as much space as 
    possible, or a specific size in pixels.  The `set_default_cell_size()`
    method is also useful for controlling how space is allocated.
    """
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
    just draw them all in vertical layers.

    Use `add_front()`, `add_back()`, or `insert()` to control the order in 
    which the children widgets are layered.  `add()` is an alias for 
    `add_front()`.

    An interesting consideration with stacked widgets is whether they should be 
    treated as "opaque" or "transparent" in terms of mouse events.  In other 
    words, should mouse events just go to the upper-most widget, or should they 
    go to all the widgets?  The latter is the default, but this can be changed 
    by setting `custom_one_child_gets_mouse = True`.
    """

    custom_one_child_gets_mouse = False
    """
    If `True`, each mouse event will be propagated only to the upper-most 
    widget under the mouse.  Note that if the stack contains widgets of 
    different sizes, the "upper-most widget under the mouse" might not 
    be the widget on the top of the stack.  If `False`, mouse-events will be 
    propagated to all widgets.
    """

    def __init__(self):
        """
        Initialize an empty stack.
        """
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

    For example, a deck could be used to implement a roll-over effect.  (This 
    is in fact its primary purpose.)  In this case, you would create three 
    states: "base" (the default), "over" (for when the mouse is over the 
    widget), and "down" (for when the mouse is being clicked on the widget).  
    Each state would be associated with a different widget, for example an
    `Image`.  To be clear, the "states" in this example are the names "base", 
    "over", and "down".  Each of these "states" is then associated with a 
    widget.

    There are two ways to setup a deck.  The first (and most common) is via the 
    constructor, which takes an initial state and keyword arguments linking any 
    number of states with widgets.  The second is using the `add_state()` or 
    `add_states()` methods.  The `add_states_if()` method is useful if you 
    don't know a priori which states you will want to add.  For example, 
    perhaps we wouldn't want a "down" state unless we have a "down" image:
    
    >>> d = glooey.Deck('base')
    >>> d.add_states_if(
    ...         lambda w: w.image is not None,
    ...         base=glooey.Image(path_or_none),
    ...         over=glooey.Image(path_or_none),
    ...         down=glooey.Image(path_or_none),
    ... )

    Use the `set_state()` method to control which state is currently visible.
    """

    def __init__(self, initial_state, **states):
        """
        Initialize a deck.

        The `initial_state` argument is the name of the state that the deck 
        will begin in.  This can be changed at any time by calling 
        `set_state()`.  Keyword arguments can be used to associate an initial 
        set of states (keys) with widgets (values).  
        
        Note that while you must specify the initial state, you don't need to 
        immediately provide a widget that state (or any other state).  For 
        example:
        
        >>> d = glooey.Deck('base')
        >>> d.add_state('base', widget)
        """
        super().__init__()
        self._current_state = initial_state
        self._previous_state = initial_state
        self._states = {}
        self.add_states(**states)

    def __getitem__(self, state):
        """
        Get the widget associated with the given state.
        """
        return self._states[state]

    def __setitem__(self, state, widget):
        """
        Add a state to the deck.

        This is an alias for `self.add_state(state, widget)`
        """
        return self.add_state(state, widget)

    def do_claim(self):
        # Claim enough space for the biggest child, so that we won't need to 
        # repack when we change states.  (Also, I can't think of any reason why 
        # you'd want states of different sizes.)
        return claim_stacked_widgets(*self._states.values())

    def add_state(self, state, widget):
        """
        Add a state to the deck.

        If the given state already exists, it will be overwritten without error.
        """
        self._remove_state(state)
        self._add_state(state, widget)
        self._repack_and_regroup_children()

    def add_states(self, **states):
        """
        Add the given states to the deck.

        Keyword arguments map states (keys) to widgets (values).  For example:

        >>> d = glooey.Deck('base')
        >>> d.add_states(base=..., over=..., down=...)
        """
        for state, widget in states.items():
            self._remove_state(state)
            self._add_state(state, widget)
        self._repack_and_regroup_children()

    def add_states_if(self, predicate, **states):
        """
        Add any of the given states that satisfy the given predicate.

        The predicate should be callable (e.g. a function or lambda) that 
        takes one of the given widgets as an argument, and returns a boolean 
        indicating whether or not that widget should be added to the deck.  For 
        example, this could be used to exclude widgets that don't have images:

        >>> d = glooey.Deck('base')
        >>> d.add_states_if(
        ...         lambda w: w.image is not None,
        ...         base=glooey.Image(path_or_none),
        ...         over=glooey.Image(path_or_none),
        ...         down=glooey.Image(path_or_none),
        ... )
        """
        filtered_states = {
                k: w for k,w in states.items()
                if predicate(w)
        }
        self.add_states(**filtered_states)

    def reset_states(self, **states):
        """
        Remove any existing states and replace them with the ones specified in 
        the keyword arguments.

        Called without any arguments, this is an alias for `clear()`.
        """
        for state in list(self.known_states):
            self._remove_state(state)
        for state, widget in states.items():
            self._add_state(state, widget)
        self._repack_and_regroup_children()

    def reset_states_if(self, predicate, **states):
        """
        Remove any states associates with widgets that satisfy the given 
        predicate.

        See `add_states_if()` for a description of the predicate argument.
        """
        filtered_states = {
                k: w for k,w in states.items()
                if predicate(w)
        }
        self.reset_states(**filtered_states)

    def remove_state(self, state):
        """
        Remove the given state from the deck.
        """
        self.remove_states(state)

    def remove_states(self, *states):
        """
        Remove the given states from the deck.
        """
        for state in states:
            self._remove_state(state)
        self._repack_and_regroup_children()

    def clear(self):
        """
        Remove all states from the deck.
        """
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
        """
        Return the currently visible child widget.
        """
        return self._current_state

    def set_state(self, new_state):
        """
        Set the state currently being displayed by the deck.

        It is an error for the given state to not already be part of the deck.
        """
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
        """
        Set the state currently being displayed by the deck, but silently do 
        nothing if that state doesn't exist.
        """
        if new_state in self.known_states:
            self.state = new_state

    def get_widget(self, state):
        """
        Return the widget associated with the given state.
        """
        return self[state]

    def get_previous_state(self):
        """
        Return the state that was visible before the current one.

        If the current state is the only one that has ever been visible, the 
        current state itself will be returned.
        """
        return self._previous_state

    def get_known_states(self):
        """
        Return all the states currently available to the deck.
        """
        return self._states.keys()


@autoprop
class Board(Widget):

    def __init__(self):
        super().__init__()
        self._pins = {}

    def add(self, widget, **kwargs):
        # Making the pin could fail, so do it before attaching the child.
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


