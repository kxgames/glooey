#!/usr/bin/env python3

from glooey.helpers import *

def test_clamp():
    assert clamp(0, 1, 4) == 1
    assert clamp(1, 1, 4) == 1
    assert clamp(2, 1, 4) == 2
    assert clamp(3, 1, 4) == 3
    assert clamp(4, 1, 4) == 4
    assert clamp(5, 1, 4) == 4
