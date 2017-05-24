#!/usr/bin/env python3

from glooey.helpers import *

alignments = {}
def alignment(func):
    alignments[func.__name__.replace('_', ' ')] = func
    return func

@alignment
def fill(child_rect, parent_rect):
    child_rect.set(parent_rect)

@alignment
def fill_horz(child_rect, parent_rect):
    child_rect.width = parent_rect.width
    child_rect.center = parent_rect.center

@alignment
def fill_vert(child_rect, parent_rect):
    child_rect.height = parent_rect.height
    child_rect.center = parent_rect.center

@alignment
def fill_top(child_rect, parent_rect):
    child_rect.width = parent_rect.width
    child_rect.top = parent_rect.top

@alignment
def fill_bottom(child_rect, parent_rect):
    child_rect.width = parent_rect.width
    child_rect.bottom = parent_rect.bottom

@alignment
def fill_left(child_rect, parent_rect):
    child_rect.height = parent_rect.height
    child_rect.left = parent_rect.left

@alignment
def fill_right(child_rect, parent_rect):
    child_rect.height = parent_rect.height
    child_rect.right = parent_rect.right

@alignment
def top_left(child_rect, parent_rect):
    child_rect.top_left = parent_rect.top_left

@alignment
def top(child_rect, parent_rect):
    child_rect.top_center = parent_rect.top_center

@alignment
def top_right(child_rect, parent_rect):
    child_rect.top_right = parent_rect.top_right

@alignment
def left(child_rect, parent_rect):
    child_rect.center_left = parent_rect.center_left

@alignment
def center(child_rect, parent_rect):
    child_rect.center = parent_rect.center

@alignment
def right(child_rect, parent_rect):
    child_rect.center_right = parent_rect.center_right

@alignment
def bottom_left(child_rect, parent_rect):
    child_rect.bottom_left = parent_rect.bottom_left

@alignment
def bottom(child_rect, parent_rect):
    child_rect.bottom_center = parent_rect.bottom_center

@alignment
def bottom_right(child_rect, parent_rect):
    child_rect.bottom_right = parent_rect.bottom_right


def align(key_or_function, child_rect, parent_rect):
    if isinstance(key_or_function, str):
        try:
            alignment_func = alignments[key_or_function]
        except KeyError:
            newline = '\n'
            raise UsageError(f"""\
{repr(key_or_function)} is not an alignment.  Did you mean:

{newline.join('  ' + repr(k) for k in alignments)}

You can also use a function to specify an alignment, and you can register a new 
alignment string using the ``@glooey.drawing.alignment`` decorator.""")

    else:
        alignment_func = key_or_function

    alignment_func(child_rect, parent_rect)

def fixed_size_align(key_or_function, child_rect, parent_rect):
    fixed_size = child_rect.size
    align(key_or_function, child_rect, parent_rect)
    if child_rect.size != fixed_size:
        raise UsageError(f"a fixed-sized alignment was required, but {repr(key_or_function)} resized the rect being aligned from {'x'.join(fixed_size)} to {'x'.join(child_rect.size)}.")



