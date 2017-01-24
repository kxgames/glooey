#!/usr/bin/env python3

import re
from pathlib import *

icons = {
    1: {
        1: 'save',
        3: 'zoom',
        5: 'chat',
    },
    3: {
        1: 'plus',
        3: 'minus',
        5: 'left',
        7: 'right',
    },
    5: {
        1: 'yes',
        3: 'no',
        5: 'up',
        7: 'down',
    },
}

slice_pattern = re.compile('slice_(\d+)_(\d+).png')

for in_path in Path.cwd().glob('*.png'):
    slice_match = slice_pattern.match(in_path.name)
    row, col = map(int, slice_match.groups())

    try:
        icon = icons[row][col]
    except KeyError:
        in_path.unlink()
    else:
        out_path = in_path.parent / f'icon_{icon}.png'
        in_path.rename(out_path)



