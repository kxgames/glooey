#!/usr/bin/env python3

import math
import autoprop
from vecrec import Vector, Rect
from glooey.helpers import *

@autoprop
class Grid:

    def __init__(self, *, bounding_rect=None, min_cell_rects=None,
            num_rows=0, num_cols=0, padding=None, inner_padding=None, 
            outer_padding=None, row_heights=None, col_widths=None,
            default_row_height='expand', default_col_width='expand'):

        # Attributes that the user can set to affect the shape of the grid.  
        self._bounding_rect = bounding_rect or Rect.null()
        self._min_cell_rects = min_cell_rects or {}
        self._requested_num_rows = num_rows
        self._requested_num_cols = num_cols
        self._inner_padding = first_not_none((inner_padding, padding, 0))
        self._outer_padding = first_not_none((outer_padding, padding, 0))
        self._requested_row_heights = row_heights or {}
        self._requested_col_widths = col_widths or {}
        self._default_row_height = default_row_height
        self._default_col_width = default_col_width

        # Read-only attributes that reflect the current state of the grid.
        self._num_rows = 0
        self._num_cols = 0
        self._max_cell_heights = {}
        self._max_cell_widths = {}
        self._fixed_rows = set()
        self._expandable_rows = set()
        self._fixed_cols = set()
        self._expandable_cols = set()
        self._fixed_row_heights = {}
        self._fixed_col_widths = {}
        self._min_expandable_row_heights = {}
        self._min_expandable_col_widths = {}
        self._padding_height = 0
        self._padding_width = 0
        self._min_height = 0
        self._min_width = 0
        self._row_heights = {}
        self._col_widths = {}
        self._width = 0
        self._height = 0
        self._row_tops = {}
        self._col_lefts = {}
        self._cell_rects = {}

        # Attributes that manage the cache.
        self._is_shape_stale = True
        self._is_claim_stale = True
        self._are_cells_stale = True

    def make_claim(self, min_cell_rects=None):
        if min_cell_rects is not None:
            self.min_cell_rects = min_cell_rects

        self._update_claim()

        return self._min_width, self._min_height

    def make_cells(self, bounding_rect=None):
        if bounding_rect is not None:
            self.bounding_rect = bounding_rect

        self._update_cells()

        return self._cell_rects

    def find_cell_under_mouse(self, x, y):
        # The >=/<= comparisons in this method were chosen to be compatible 
        # with the comparisons in Widget.is_under_mouse().  That method counts 
        # points that are on any edge of a widget as being over that widget.  
        # The >=/<= comparisons do the same thing here.
        #
        # I initially wrote this method using an inclusive operator on one side 
        # and an exclusive one on the other, to avoid any ambiguity in the case 
        # where there's no padding.  For example, imagine a 2x2 grid with no 
        # padding.  In theory, the point exactly in the middle is over all four 
        # cells.  In practice, the algorithm will identify the top-left-most 
        # cell first and return it.  So the algorithm isn't really ambiguous, 
        # but it is more dependent on what's really an implementation detail.

        # Find the row the mouse is over.
        for i in range(self._num_rows):
            row_top = self._row_tops[i]
            row_bottom = row_top - self._row_heights[i]
            if row_top >= y >= row_bottom:
                break
        else:
            return None

        # Find the col the mouse is over.
        for j in range(self._num_cols):
            col_left = self._col_lefts[j]
            col_right = col_left + self._col_widths[j]
            if col_left <= x <= col_right:
                break
        else:
            return None

        return i, j

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_rect(self):
        return Rect.from_size(self._width, self._height)

    def get_min_width(self):
        return self._min_width

    def get_min_height(self):
        return self._min_height

    min_height = property(get_min_height)

    def get_min_bounding_rect(self):
        return Rect.from_size(self._min_width, self._min_height)

    def get_cell_rects(self):
        return self._cell_rects

    cell_rects = property(get_cell_rects)

    def get_bounding_rect(self):
        return self._bounding_rect

    def set_bounding_rect(self, new_rect):
        if self._bounding_rect != new_rect:
            self._bounding_rect = new_rect
            self._invalidate_cells()

    def get_min_cell_rect(self, i, j):
        return self._min_cell_rects[i,j]

    def set_min_cell_rect(self, i, j, new_rect):
        if (i,j) not in self._min_cell_rects or \
                self._min_cell_rects[i,j] != new_rect:
            self._min_cell_rects[i,j] = new_rect
            self._invalidate_shape()

    def del_min_cell_rect(self, i, j):
        if (i,j) in self._min_cell_rects:
            del self._min_cell_rects[i,j]
            self._invalidate_shape()

    def get_min_cell_rects(self):
        return self._min_cell_rects

    def set_min_cell_rects(self, new_rects):
        if self._min_cell_rects != new_rects:
            self._min_cell_rects = new_rects
            self._invalidate_shape()

    def del_min_cell_rects(self):
        if self._min_cell_rects:
            self._min_cell_rects = {}
            self._invalidate_shape()

    def get_num_rows(self):
        return self._num_rows

    def set_num_rows(self, new_num):
        self._requested_num_rows = new_num
        self._invalidate_shape()

    def get_num_cols(self):
        return self._num_cols

    def set_num_cols(self, new_num):
        self._requested_num_cols = new_num
        self._invalidate_shape()

    def get_padding(self):
        return self._inner_padding, self._outer_padding

    def set_padding(self, new_padding):
        self._inner_padding = new_padding
        self._outer_padding = new_padding
        self._invalidate_claim()

    def get_inner_padding(self):
        return self._inner_padding

    def set_inner_padding(self, new_padding):
        self._inner_padding = new_padding
        self._invalidate_claim()

    def get_outer_padding(self):
        return self._outer_padding

    def set_outer_padding(self, new_padding):
        self._outer_padding = new_padding
        self._invalidate_claim()

    def get_row_height(self, i):
        return self._row_heights[i]

    def set_row_height(self, i, new_height):
        self._requested_row_heights[i] = new_height
        self._invalidate_claim()

    def del_row_height(self, i):
        if i in self._requested_row_heights:
            del self._requested_row_heights[i]
            self._invalidate_claim()

    def get_row_heights(self):
        return self._row_heights

    def set_row_heights(self, new_heights):
        self._requested_row_heights = new_heights
        self._invalidate_claim()

    def del_row_heights(self):
        self._requested_row_heights = {}
        self._invalidate_claim()

    def get_col_width(self, j):
        return self._col_widths[j]

    def set_col_width(self, j, new_width):
        self._requested_col_widths[j] = new_width
        self._invalidate_claim()

    def del_col_width(self, j):
        if j in self._requested_col_widths:
            del self._requested_col_widths[j]
            self._invalidate_claim()

    def get_col_widths(self):
        return self._col_widths

    def set_col_widths(self, new_widths):
        self._requested_col_widths = new_widths
        self._invalidate_claim()

    def del_col_widths(self):
        self._requested_col_widths = {}
        self._invalidate_claim()

    def get_default_row_height(self):
        return self._default_row_height

    def set_default_row_height(self, new_height):
        self._default_row_height = new_height
        self._invalidate_claim()

    def get_default_col_width(self):
        return self._default_col_width

    def set_default_col_width(self, new_width):
        self._default_col_width = new_width
        self._invalidate_claim()

    def get_requested_num_rows(self):
        return self._requested_num_rows

    def get_requested_num_cols(self):
        return self._requested_num_cols

    requested_num_cols = property(get_requested_num_cols)

    def get_requested_row_height(self, i):
        return self._requested_row_heights[i]

    def get_requested_row_heights(self):
        return self._requested_row_heights

    def get_requested_col_width(self, i):
        return self._requested_col_widths[i]

    def get_requested_col_widths(self):
        return self._requested_col_widths

    def _invalidate_shape(self):
        self._is_shape_stale = True
        self._invalidate_claim()

    def _invalidate_claim(self):
        self._is_claim_stale = True
        self._invalidate_cells()

    def _invalidate_cells(self):
        self._are_cells_stale = True

    def _update_shape(self):
        if self._is_shape_stale:
            self._find_num_rows()
            self._find_num_cols()
            self._find_max_cell_dimensions()
            self.is_shape_stale = False

    def _update_claim(self):
        if self._is_claim_stale:
            self._update_shape()
            self._find_which_rows_expand()
            self._find_which_cols_expand()
            self._find_fixed_row_heights()
            self._find_fixed_col_widths()
            self._find_min_expandable_row_heights()
            self._find_min_expandable_col_widths()
            self._find_padding_height()
            self._find_padding_width()
            self._find_min_height()
            self._find_min_width()
            self._is_claim_stale = False

    def _update_cells(self):
        if self._are_cells_stale:
            self._update_claim()

            if self._bounding_rect.width < self._min_width:
                raise UsageError("grid cannot fit in {0[0]}x{0[1]}, need to be at least {1} px wide.".format(self._bounding_rect.size, self._min_width))
            if self._bounding_rect.height < self._min_height:
                raise UsageError("grid cannot fit in {0[0]}x{0[1]}, need to be at least {1} px tall.".format(self._bounding_rect.size, self._min_height))

            self._find_row_heights()
            self._find_col_widths()
            self._find_cell_rects()
            self._are_cells_stale = False

    def _find_num_rows(self):
        min_num_rows = 0
        for i,j in self._min_cell_rects:
            min_num_rows = max(i+1, min_num_rows)

        if self._requested_num_rows:
            self._num_rows = self._requested_num_rows
        else:
            self._num_rows = min_num_rows

        if self._num_rows < min_num_rows:
            raise UsageError("not enough rows requested")

    def _find_num_cols(self):
        min_num_cols = 0
        for i,j in self._min_cell_rects:
            min_num_cols = max(j+1, min_num_cols)

        if self._requested_num_cols:
            self._num_cols = self._requested_num_cols
        else:
            self._num_cols = min_num_cols

        if self._num_cols < min_num_cols:
            raise UsageError("not enough columns requested")

    def _find_max_cell_dimensions(self):
        """
        Find the tallest and widest cell in each dimension.
        """
        self._max_cell_heights = {}
        self._max_cell_widths = {}

        for i,j in self._min_cell_rects:
            # Use -math.inf so that negative cell sizes can be used.
            self._max_cell_heights[i] = max(
                    self._min_cell_rects[i,j].height,
                    self._max_cell_heights.get(i, -math.inf))
            self._max_cell_widths[j] = max(
                    self._min_cell_rects[i,j].width,
                    self._max_cell_widths.get(j, -math.inf))

    def _find_which_rows_expand(self):
        self._fixed_rows = set()
        self._expandable_rows = set()

        for i in range(self._num_rows):
            size_request = self._get_requested_row_height(i)

            if isinstance(size_request, int):
                self._fixed_rows.add(i)
            elif size_request == 'expand':
                self._expandable_rows.add(i)
            else:
                raise UsageError("illegal row height: {}".format(repr(size_request)))

        self._num_fixed_rows = len(self._fixed_rows)
        self._num_expandable_rows = len(self._expandable_rows)

    def _find_which_cols_expand(self):
        self._fixed_cols = set()
        self._expandable_cols = set()

        for j in range(self._num_cols):
            size_request = self._get_requested_col_width(j)

            if isinstance(size_request, int):
                self._fixed_cols.add(j)
            elif size_request == 'expand':
                self._expandable_cols.add(j)
            else:
                raise UsageError("illegal col width: {}".format(repr(size_request)))

        self._num_fixed_cols = len(self._fixed_cols)
        self._num_expandable_cols = len(self._expandable_cols)

    def _find_fixed_row_heights(self):
        self._fixed_row_heights = {}
        for i in self._fixed_rows:
            # Use -math.inf so that negative cell sizes can be used.
            self._fixed_row_heights[i] = max(
                    self._get_requested_row_height(i),
                    self._max_cell_heights.get(i, -math.inf))

    def _find_fixed_col_widths(self):
        self._fixed_col_widths = {}
        for j in self._fixed_cols:
            # Use -math.inf so that negative cell sizes can be used.
            self._fixed_col_widths[j] = max(
                    self._get_requested_col_width(j),
                    self._max_cell_widths.get(j, -math.inf))

    def _find_min_expandable_row_heights(self):
        self._min_expandable_row_heights = {}
        for i in self._expandable_rows:
            self._min_expandable_row_heights[i] = \
                    self._max_cell_heights.get(i, 0)

    def _find_min_expandable_col_widths(self):
        self._min_expandable_col_widths = {}
        for j in self._expandable_cols:
            self._min_expandable_col_widths[j] = \
                    self._max_cell_widths.get(j, 0)

    def _find_padding_height(self):
        self._padding_height = \
                + self._inner_padding * (self._num_rows - 1) \
                + self._outer_padding * 2

    def _find_padding_width(self):
        self._padding_width = \
                + self._inner_padding * (self._num_cols - 1) \
                + self._outer_padding * 2

    def _find_min_height(self):
        min_expandable_height = max(
                self._min_expandable_row_heights.values() or [0])
        self._min_height = \
                + sum(self._fixed_row_heights.values()) \
                + min_expandable_height * self._num_expandable_rows \
                + self._padding_height

    def _find_min_width(self):
        min_expandable_width = max(
                self._min_expandable_col_widths.values() or [0])
        self._min_width = \
                + sum(self._fixed_col_widths.values()) \
                + min_expandable_width * self._num_expandable_cols \
                + self._padding_width

    def _find_row_heights(self):
        self._row_heights = self._fixed_row_heights.copy()

        if self._num_expandable_rows:
            expandable_row_height = (
                    + self._bounding_rect.height
                    - sum(self._fixed_row_heights.values())
                    - self._padding_height
                    ) / self._num_expandable_rows

            for i in self._expandable_rows:
                self._row_heights[i] = expandable_row_height

        self._height = \
                + sum(self._row_heights.values()) \
                + self._padding_height

    def _find_col_widths(self):
        self._col_widths = self._fixed_col_widths.copy()

        if self._num_expandable_cols:
            expandable_col_width = (
                    + self._bounding_rect.width
                    - sum(self._fixed_col_widths.values())
                    - self._padding_width
                    ) / self._num_expandable_cols

            for j in self._expandable_cols:
                self._col_widths[j] = expandable_col_width

        self._width = \
                + sum(self._col_widths.values()) \
                + self._padding_width

    def _find_cell_rects(self):
        self._row_tops = {}
        self._col_lefts = {}
        self._cell_rects = {}

        top_cursor = self._bounding_rect.top

        for i in range(self._num_rows):
            top_cursor -= self._get_row_padding(i)
            left_cursor = self._bounding_rect.left
            row_height = self._row_heights[i]
            self._row_tops[i] = top_cursor

            for j in range(self._num_cols):
                left_cursor += self._get_col_padding(j)
                col_width = self._col_widths[j]

                self._cell_rects[i,j] = Rect.from_size(col_width, row_height)
                self._cell_rects[i,j].top_left = left_cursor, top_cursor
                self._col_lefts[j] = left_cursor

                left_cursor += col_width
            top_cursor -= row_height

    def _get_requested_row_height(self, i):
        return self._requested_row_heights.get(i, self._default_row_height)

    def _get_requested_col_width(self, j):
        return self._requested_col_widths.get(j, self._default_col_width)

    def _get_row_padding(self, i):
        return self._outer_padding if i == 0 else self._inner_padding

    def _get_col_padding(self, j):
        return self._outer_padding if j == 0 else self._inner_padding

def make_grid(rect, cells={}, num_rows=0, num_cols=0, padding=None,
        inner_padding=None, outer_padding=None, row_heights={}, col_widths={}, 
        default_row_height='expand', default_col_width='expand'):
    """
    Return rectangles for each cell in the specified grid.  The rectangles are 
    returned in a dictionary where the keys are (row, col) tuples.
    """
    grid = Grid(
            bounding_rect=rect,
            min_cell_rects=cells,
            num_rows=num_rows,
            num_cols=num_cols,
            padding=padding,
            inner_padding=inner_padding,
            outer_padding=outer_padding,
            row_heights=row_heights,
            col_widths=col_widths,
            default_row_height=default_row_height,
            default_col_width=default_col_width,
    )
    return grid.make_cells()

