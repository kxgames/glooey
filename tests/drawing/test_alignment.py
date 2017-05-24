#!/usr/bin/env python3

import pytest
import glooey

def test_misspelled_alignment():
    with pytest.raises(glooey.UsageError) as err:
        glooey.drawing.align('not an alignment', None, None)

