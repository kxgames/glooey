#!/usr/bin/env python3

import pytest
import glooey
from vecrec import Rect

def test_misspelled_alignment():
    with pytest.raises(glooey.UsageError) as err:
        glooey.drawing.align('not an alignment', None, None)

def test_parent_changed():
    child, parent = Rect.null(), Rect.null()

    def change_parent(child_rect, parent_rect):
        parent_rect.left += 1

    with pytest.raises(RuntimeError, match='change_parent'):
        glooey.drawing.align(change_parent, child, parent)

def test_child_outside_parent():
    child = Rect.from_square(5)
    parent = Rect.from_square(6)

    def move_1px_right(child_rect, parent_rect):
        child_rect.left += 1

    # This should be fine the first time...
    glooey.drawing.align(move_1px_right, child, parent)

    # ...but out-of-bounds the second time.
    with pytest.raises(RuntimeError, match='move_1px_right'):
        glooey.drawing.align(move_1px_right, child, parent)
    
