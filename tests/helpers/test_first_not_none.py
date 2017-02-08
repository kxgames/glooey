#!/usr/bin/env python3

from glooey.helpers import first_not_none

def test_first_not_none():
    assert first_not_none((1, 0, None)) == 1
    assert first_not_none((0, 1, None)) == 0
    assert first_not_none((1, None, 0)) == 1
    assert first_not_none((0, None, 1)) == 0
    assert first_not_none((None, 1, 0)) == 1
    assert first_not_none((None, 0, 1)) == 0
