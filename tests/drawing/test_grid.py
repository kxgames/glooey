#!/usr/bin/env python3

import pytest
from vecrec import Rect
from glooey import drawing, UsageError

def test_no_cells():
    cells = drawing.make_grid(
            Rect.null()
    )
    assert cells == {}

def test_one_cell():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
    )
    assert cells == {
            (0,0): Rect(0, 0, 10, 10),
    }

def test_two_cells():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
    )
    assert cells == {
            (0,0): Rect(0, 5, 10, 5),
            (1,0): Rect(0, 0, 10, 5),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
    )
    assert cells == {
            (0,0): Rect(0, 0, 5, 10),
            (0,1): Rect(5, 0, 5, 10),
    }

def test_padding():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
            padding=1,
    )
    assert cells == {
            (0,0): Rect(1, 1, 8, 8),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 11),
            num_rows=2,
            num_cols=1,
            padding=1,
    )
    assert cells == {
            (0,0): Rect(1, 6, 8, 4),
            (1,0): Rect(1, 1, 8, 4),
    }

    cells = drawing.make_grid(
            Rect.from_size(11, 10),
            num_rows=1,
            num_cols=2,
            padding=1
    )
    assert cells == {
            (0,0): Rect(1, 1, 4, 8),
            (0,1): Rect(6, 1, 4, 8),
    }

def test_inner_padding():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
            inner_padding=1,
    )
    assert cells == {
            (0,0): Rect(0, 0, 10, 10),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 11),
            num_rows=2,
            num_cols=1,
            inner_padding=1,
    )
    assert cells == {
            (0,0): Rect(0, 6, 10, 5),
            (1,0): Rect(0, 0, 10, 5),
    }

    cells = drawing.make_grid(
            Rect.from_size(11, 10),
            num_rows=1,
            num_cols=2,
            inner_padding=1
    )
    assert cells == {
            (0,0): Rect(0, 0, 5, 10),
            (0,1): Rect(6, 0, 5, 10),
    }

def test_outer_padding():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
            outer_padding=1,
    )
    assert cells == {
            (0,0): Rect(1, 1, 8, 8),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            outer_padding=1,
    )
    assert cells == {
            (0,0): Rect(1, 5, 8, 4),
            (1,0): Rect(1, 1, 8, 4),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            outer_padding=1
    )
    assert cells == {
            (0,0): Rect(1, 1, 4, 8),
            (0,1): Rect(5, 1, 4, 8),
    }

def test_request_row_height():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            row_heights={0: 2},
    )
    assert cells == {
            (0,0): Rect(0, 8, 10, 2),
            (1,0): Rect(0, 0, 10, 8),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            row_heights={1: 2},
    )
    assert cells == {
            (0,0): Rect(0, 2, 10, 8),
            (1,0): Rect(0, 0, 10, 2),
    }

def test_request_col_width():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            col_widths={0: 2},
    )
    assert cells == {
            (0,0): Rect(0, 0, 2, 10),
            (0,1): Rect(2, 0, 8, 10),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            col_widths={1: 2},
    )
    assert cells == {
            (0,0): Rect(0, 0, 8, 10),
            (0,1): Rect(8, 0, 2, 10),
    }

def test_default_row_height():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            row_heights={0: 'expand'},
            default_row_height=2,
    )
    assert cells == {
            (0,0): Rect(0, 2, 10, 8),
            (1,0): Rect(0, 0, 10, 2),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            row_heights={1: 'expand'},
            default_row_height=2,
    )
    assert cells == {
            (0,0): Rect(0, 8, 10, 2),
            (1,0): Rect(0, 0, 10, 8),
    }

def test_default_col_width():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            col_widths={0: 'expand'},
            default_col_width=2,
    )
    assert cells == {
            (0,0): Rect(0, 0, 8, 10),
            (0,1): Rect(8, 0, 2, 10),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            col_widths={1: 'expand'},
            default_col_width=2,
    )
    assert cells == {
            (0,0): Rect(0, 0, 2, 10),
            (0,1): Rect(2, 0, 8, 10),
    }

def test_infer_grid_size():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.null(),
            },
    )
    assert cells == {
            (0,0): Rect(0, 0, 10, 10),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.null(),
                (1,0): Rect.null(),
            },
    )
    assert cells == {
            (0,0): Rect(0, 5, 10, 5),
            (1,0): Rect(0, 0, 10, 5),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.null(),
                (0,1): Rect.null(),
            },
    )
    assert cells == {
            (0,0): Rect(0, 0, 5, 10),
            (0,1): Rect(5, 0, 5, 10),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.null(),
                (1,1): Rect.null(),
            },
    )
    assert cells == {
            (0,0): Rect(0, 5, 5, 5),
            (0,1): Rect(5, 5, 5, 5),
            (1,0): Rect(0, 0, 5, 5),
            (1,1): Rect(5, 0, 5, 5),
    }

def test_min_cell_rect_vs_row_height():
    # If there is a cell larger than the specified row height, make the row big 
    # enough to fit that cell.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2,2),
            },
            num_rows=2,
            num_cols=1,
            row_heights={0: 0},
    )
    assert cells == {
            (0,0): Rect(0, 8, 10, 2),
            (1,0): Rect(0, 0, 10, 8),
    }

    # If the specified row height is larger than any of the cells in the row, 
    # make the row the specified height.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2,2),
            },
            num_rows=2,
            num_cols=1,
            row_heights={0: 4},
    )
    assert cells == {
            (0,0): Rect(0, 6, 10, 4),
            (1,0): Rect(0, 0, 10, 6),
    }

    # If there are multiple cells in the row, the row should be big enough for 
    # all of them.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2,2),
                (0,1): Rect.from_size(4,4),
            },
            num_rows=2,
            num_cols=2,
            row_heights={0: 0},
    )
    assert cells == {
            (0,0): Rect(0, 6, 5, 4),
            (0,1): Rect(5, 6, 5, 4),
            (1,0): Rect(0, 0, 5, 6),
            (1,1): Rect(5, 0, 5, 6),
    }

def test_min_cell_rect_vs_col_width():
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2,2),
            },
            num_rows=1,
            num_cols=2,
            col_widths={0: 0},
    )
    assert cells == {
            (0,0): Rect(0, 0, 2, 10),
            (0,1): Rect(2, 0, 8, 10),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2,2),
            },
            num_rows=1,
            num_cols=2,
            col_widths={0: 4},
    )
    assert cells == {
            (0,0): Rect(0, 0, 4, 10),
            (0,1): Rect(4, 0, 6, 10),
    }

    # If there are multiple cells in the column, the column should be big 
    # enough for all of them.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2,2),
                (1,0): Rect.from_size(4,4),
            },
            num_rows=2,
            num_cols=2,
            col_widths={0: 0},
    )
    assert cells == {
            (0,0): Rect(0, 5, 4, 5),
            (1,0): Rect(0, 0, 4, 5),
            (0,1): Rect(4, 5, 6, 5),
            (1,1): Rect(4, 0, 6, 5),
    }

def test_make_claim():
    grid = drawing.Grid()
    cells = {
        (0,0): Rect.from_size(1, 2),
        (1,1): Rect.from_size(3, 4),
    }
    assert grid.make_claim(cells) == (6, 8)
    assert grid.make_claim() == (6, 8)
    assert grid.min_width == 6
    assert grid.min_height == 8
    assert grid.min_bounding_rect == Rect(0, 0, 6, 8)

    grid.default_row_height = 0
    grid.default_col_width = 0

    assert grid.make_claim(cells) == (4, 6)
    assert grid.make_claim() == (4, 6)
    assert grid.min_width == 4
    assert grid.min_height == 6
    assert grid.min_bounding_rect == Rect(0, 0, 4, 6)

def test_make_cells():
    grid = drawing.Grid()
    grid.num_rows = 2
    grid.num_cols = 2
    
    expected_results = [(
        Rect.from_size(10, 10), {
            (0, 0): Rect(0, 5, 5, 5),
            (0, 1): Rect(5, 5, 5, 5),
            (1, 0): Rect(0, 0, 5, 5),
            (1, 1): Rect(5, 0, 5, 5),
        }),(
        Rect.from_size(20, 20), {
            (0, 0): Rect(0,  10, 10, 10),
            (0, 1): Rect(10, 10, 10, 10),
            (1, 0): Rect(0,   0, 10, 10),
            (1, 1): Rect(10,  0, 10, 10),
        }),
    ]
    for bbox, cells in expected_results:
        assert grid.make_cells(bbox) == cells
        assert grid.make_cells() == cells
        assert grid.cell_rects == cells
        assert grid.bounding_rect == bbox

def test_find_cell_under_mouse():
    grid = drawing.Grid()
    grid.num_rows = 2
    grid.num_cols = 2
    grid.padding = 1
    grid.make_cells(Rect.from_size(5, 5))

    expected_results = {
            (0, 0): None,
            (0, 1): None,
            (0, 2): None,
            (0, 3): None,
            (0, 4): None,

            (1, 0): None,
            (1, 1): (1, 0),
            (1, 2): (1, 0),
            (1, 3): (0, 0),
            (1, 4): (0, 0),

            (2, 0): None,
            (2, 1): (1, 0),
            (2, 2): (1, 0),
            (2, 3): (0, 0),
            (2, 4): (0, 0),

            (3, 0): None,
            (3, 1): (1, 1),
            (3, 2): (1, 1),
            (3, 3): (0, 1),
            (3, 4): (0, 1),

            (4, 0): None,
            (4, 1): (1, 1),
            (4, 2): (1, 1),
            (4, 3): (0, 1),
            (4, 4): (0, 1),
    }
    for mouse, cell in expected_results.items():
        assert grid.find_cell_under_mouse(*mouse) == cell

def test_setters():
    grid = drawing.Grid()
    assert grid.make_claim() == (0, 0)

    grid.num_rows = 1
    grid.default_row_height = 10
    assert grid.make_claim() == (0, 10)

    grid.num_cols = 1
    grid.default_col_width = 10
    assert grid.make_claim() == (10, 10)

    grid.padding = 1
    assert grid.make_claim() == (12, 12)

    grid.num_rows = 2
    grid.num_cols = 2
    assert grid.make_claim() == (23, 23)

    grid.set_min_cell_rects({(0,0): Rect.from_size(20, 20)})
    assert grid.make_claim() == (33, 33)

    grid.del_min_cell_rects()
    assert grid.make_claim() == (23, 23)

    grid.set_min_cell_rect(0, 0, Rect.from_size(20, 20))
    assert grid.make_claim() == (33, 33)

    grid.del_min_cell_rect(0, 0)
    assert grid.make_claim() == (23, 23)

    grid.set_row_height(0, 20)
    assert grid.make_claim() == (23, 33)

    grid.del_row_height(0)
    assert grid.make_claim() == (23, 23)

    grid.set_col_width(0, 20)
    assert grid.make_claim() == (33, 23)

    grid.del_col_width(0)
    assert grid.make_claim() == (23, 23)

def test_negative_sizes():
    # Initially I thought this should be an error, but then I decided that it 
    # probably just works as you'd expect it to, and it might be a useful way 
    # to create an overlapping effect or to get rid of padding in certain 
    # places.

    # row_heights can be negative.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            row_heights={0: -2},
    )
    assert cells == {
            (0,0): Rect(0, 12, 10, -2),
            (1,0): Rect(0,  0, 10, 12),
    }

    # default_row_height can be negative.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=2,
            num_cols=1,
            row_heights={1: 'expand'},
            default_row_height=-2,
    )
    assert cells == {
            (0,0): Rect(0, 12, 10, -2),
            (1,0): Rect(0,  0, 10, 12),
    }

    # col_widths can be negative.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            col_widths={0: -2},
    )
    assert cells == {
            (0,0): Rect(0, 0, -2, 10),
            (0,1): Rect(-2, 0, 12, 10),
    }

    # default_col_width can be negative.
    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=2,
            col_widths={1: 'expand'},
            default_col_width=-2,
    )
    assert cells == {
            (0,0): Rect(0, 0, -2, 10),
            (0,1): Rect(-2, 0, 12, 10),
    }
def test_no_expandable_cells():
    # If the grid can't fill all the space made available to it, it will pack 
    # against the top-left corner.  I chose this corner arbitrarily (although 
    # other corners would've been slightly harder to implement).  I decided 
    # against adding the ability to control how the grid fits in its bounding 
    # box for two reasons.  First, you can get the same effect by simply adding 
    # expandable rows or columns.  Second, you can just change the bounding 
    # box.  Still, it's possible I'll change my mind about this behavior.

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
            row_heights={0: 2},
            col_widths={0: 2},
    )
    assert cells == {
            (0,0): Rect(0, 8, 2, 2),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
            default_row_height=2,
            default_col_width=2,
    )
    assert cells == {
            (0,0): Rect(0, 8, 2, 2),
    }

    cells = drawing.make_grid(
            Rect.from_size(10, 10),
            cells={
                (0,0): Rect.from_size(2, 2),
            },
            default_row_height=0,
            default_col_width=0,
    )
    assert cells == {
            (0,0): Rect(0, 8, 2, 2),
    }

def test_bounding_rect_too_small():
    # Just big enough, should not raise.
    drawing.make_grid(
            Rect.from_size(10, 10),
            num_rows=1,
            num_cols=1,
            default_row_height=10,
            default_col_width=10,
    )
    # Too narrow.
    with pytest.raises(UsageError):
        drawing.make_grid(
                Rect.from_size(9, 10),
                num_rows=1,
                num_cols=1,
                default_row_height=10,
                default_col_width=10,
        )
    # Too short.
    with pytest.raises(UsageError):
        drawing.make_grid(
                Rect.from_size(10, 9),
                num_rows=1,
                num_cols=1,
                default_row_height=10,
                default_col_width=10,
        )

def test_not_enough_rows():
    with pytest.raises(UsageError):
        drawing.make_grid(
                Rect.null(),
                cells={
                    (1,0): Rect.null(),
                },
                num_rows=1,
                num_cols=1,
        )

def test_not_enough_cols():
    with pytest.raises(UsageError):
        drawing.make_grid(
                Rect.null(),
                cells={
                    (0,1): Rect.null(),
                },
                num_rows=1,
                num_cols=1,
        )

def test_real_examples():
    cells = drawing.make_grid(
            Rect.from_size(640, 480),
            cells={
                (0,0): Rect(0, 0,  10, 10),
                (0,1): Rect(0, 0, 310, 10),
                (0,2): Rect(0, 0,  10, 10),
                (0,3): Rect(0, 0,  10, 10),
            },
            col_widths={1: 0},
    )
    assert cells == {
            (0,0): Rect(  0, 0, 110, 480),
            (0,1): Rect(110, 0, 310, 480),
            (0,2): Rect(420, 0, 110, 480),
            (0,3): Rect(530, 0, 110, 480),
    }

def test_no_shared_state():
    """
    See issue #11.
    """
    grid_1 = drawing.Grid()
    grid_2 = drawing.Grid()
    i, j = 0, 0

    grid_1.set_row_height(i, 1)
    grid_2.set_row_height(i, 2)

    assert grid_1.get_requested_row_height(i) == 1
    assert grid_2.get_requested_row_height(i) == 2

    grid_1.set_col_width(j, 1)
    grid_2.set_col_width(j, 2)

    assert grid_1.get_requested_col_width(j) == 1
    assert grid_2.get_requested_col_width(j) == 2

    rect_1, rect_2 = Rect.from_size(1, 1), Rect.from_size(2, 2)
    assert rect_1 is not rect_2

    grid_1.set_min_cell_rect(i, j, rect_1)
    grid_2.set_min_cell_rect(i, j, rect_2)

    assert grid_1.get_min_cell_rect(i, j) is rect_1
    assert grid_2.get_min_cell_rect(i, j) is rect_2

    

