#!/usr/bin/env python3

import glooey
import autoprop
from glooey.helpers import *

@autoprop
class Color:
    # Right now, the color class's internal representation is integers.  I 
    # don't know if this is a good thing, because integers aren't as expressive 
    # as floats.  This surprised me when I tried to use __truediv__ to 
    # implement get_float().  It didn't work because the RGBA values got 
    # converted to ints before being returned.

    @staticmethod
    def from_anything(color):
        if isinstance(color, Color):
            return color

        if isinstance(color, str):
            return Color.from_str(color)

        if isinstance(color, tuple):
            if all(0 <= x <= 1 and isinstance(x, float) for x in color):
                return Color.from_float_tuple(color)
            else:
                return Color.from_int_tuple(color)

        raise ValueError(f"cannot convert {repr(color)} to color")

    @staticmethod
    def from_str(str):
        # If the given string is to the name of a known color, return that 
        # color.  Otherwise, treat the string as a hex code.
        if str in glooey.drawing.colors:
            return glooey.drawing.colors[str]
        else:
            return Color.from_hex(str)

    @staticmethod
    def from_hex(hex):
        import re

        hex_digits = '([0-9a-fA-f]{2})'
        hex_pattern = '#?' + (3 * hex_digits) + (hex_digits + '?')
        hex_match = re.match(hex_pattern, hex)

        if hex_match:
            hex_ints = [int(x, 16) for x in hex_match.groups() if x is not None]
            return Color.from_int_tuple(hex_ints)
        else:
            raise ValueError("Couldn't interpret '{}' as a hex color.".format(hex))

    @staticmethod
    def from_ints(red, green, blue, alpha=255):
        return Color(red, green, blue, alpha)

    @staticmethod
    def from_int_tuple(rgba):
        return Color(*rgba)

    @staticmethod
    def from_floats(red, green, blue, alpha=1.0):
        return Color(255 * red, 255 * green, 255 * blue, 255 * alpha)

    @staticmethod
    def from_float_tuple(rgba):
        return Color.from_floats(*rgba)


    def __init__(self, red, green, blue, alpha=255):
        self.r = red
        self.g = green
        self.b = blue
        self.a = alpha

    def __iter__(self):
        return iter(self.tuple)

    def __str__(self):
        return '#%02x%02x%02x%02x' % self.tuple

    def __repr__(self):
        return 'Color({0.red}, {0.green}, {0.blue}, {0.alpha})'.format(self)


    def __add__(self, other):
        return Color(
                self.r + other.r,
                self.g + other.g,
                self.b + other.b,
                self.a + other.a)

    def __sub__(self, other):
        return Color(
                self.r - other.r,
                self.g - other.g,
                self.b - other.b,
                self.a - other.a)

    def __mul__(self, scalar):
        return Color(
                scalar * self.r,
                scalar * self.g,
                scalar * self.b,
                scalar * self.a)

    def __truediv__(self, scalar):
        return Color(
                self.r / scalar,
                self.g / scalar,
                self.b / scalar,
                self.a / scalar)


    def get_red(self):
        return self.r

    def get_green(self):
        return self.g

    def get_blue(self):
        return self.b

    def get_alpha(self):
        return self.a

    def get_rgb(self):
        return self.r, self.g, self.b

    def get_rgba(self):
        return self.r, self.g, self.b, self.a

    def get_tuple(self):
        return self.rgba
    
    def get_float(self):
        return (self.r / 255,
                self.g / 255,
                self.b / 255,
                self.a / 255)


    def set_red(self, red):
        self.r = int(min(max(red, 0), 255))

    def set_green(self, green):
        self.g = int(min(max(green, 0), 255))

    def set_blue(self, blue):
        self.b = int(min(max(blue, 0), 255))

    def set_alpha(self, alpha):
        self.a = int(min(max(alpha, 0), 255))

    def set_rgb(self, red, green, blue):
        self.r, self.g, self.b = red, green, blue

    def set_rgba(self, red, green, blue, alpha):
        self.r, self.g, self.b, self.a = red, green, blue, alpha

    def set_tuple(self, red, green, blue, alpha):
        self.set_rgba(red, green, blue, alpha)

    def set_float(self, red, green, blue, alpha):
        self.r = int(255 * red)
        self.g = int(255 * green)
        self.b = int(255 * blue)
        self.a = int(255 * alpha)


    def lighten(self, extent):
        self.interpolate(white, extent)

    def darken(self, extent):
        self.interpolate(black, extent)

    def disappear(self, extent):
        self.alpha = extent * self.alpha

    def interpolate(self, target, extent):
        self += extent * (target - self)

def hex_to_float(hex):
    return Color.from_hex(hex).float

def hex_to_int(hex):
    return Color.from_hex(hex).tuple

colors = {
        'red': Color(164, 0, 0),
        'brown': Color(143, 89, 2),
        'orange': Color(206, 92, 0),
        'yellow': Color(196, 160, 0),
        'green': Color(78, 154, 6),
        'blue': Color(32, 74, 135),
        'purple': Color(92, 53, 102),
        'black': Color(0, 0, 0),
        'dark': Color(46, 52, 54),
        'gray': Color(85, 87, 83),
        'light': Color(255, 250, 240),
        'white': Color(255, 255, 255),
}

def set_colors(new_colors):
    """
    Change the set of named colors recognized by glooey.
    """
    colors.clear()
    colors.update(new_colors)

