#!/usr/bin/env python3

import glooey
import pytest

@pytest.mark.parametrize(
        ('args',   'expected'), [

        ([1],               1),
        ([0],               0),
        ([1, None],         1),
        ([0, None],         0),
        ([None, 1],         1),
        ([None, 0],         0),

        ([1, None, None],   1),
        ([0, None, None],   0),
        ([None, 1, None],   1),
        ([None, 0, None],   0),
        ([None, None, 1],   1),
        ([None, None, 0],   0),

        ([1, 0],            1),
        ([0, 1],            0),
        ([None, 1, 0],      1),
        ([None, 0, 1],      0),
        ([1, None, 0],      1),
        ([0, None, 1],      0),
        ([1, 0, None],      1),
        ([0, 1, None],      0),

])
def test_basic_usage(args, expected):
    assert glooey.first_not_none(args) == expected

@pytest.mark.parametrize(
        ('args',        'err'), [
        ([],            "No values"),
        ([None],        "1 values"),
        ([None, None],  "2 values"),
])
def test_bad_inputs(args, err):
    with pytest.raises(ValueError, match=err):
        glooey.first_not_none(args)

