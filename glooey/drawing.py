import math
import pyglet
import more_itertools

from pyglet.gl import *
from pyglet.graphics import Group, OrderedGroup
from vecrec import Vector, Rect

# Color utilities

# Right now, the color class's internal representation is integers.  I don't 
# know if this is a good thing, because integers aren't as expressive as 
# floats.  This surprised me when I tried to use __truediv__ to implement 
# get_float().  It didn't work because the RGBA values got converted to ints 
# before being returned.

class Color (object):

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
        return Color(255 * red, 255 * green, 255 * blue)

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
        return self._red

    def get_green(self):
        return self._green

    def get_blue(self):
        return self._blue

    def get_alpha(self):
        return self._alpha

    def get_tuple(self):
        return self.r, self.g, self.b, self.a
    
    def get_float(self):
        return (self.r / 255,
                self.g / 255,
                self.b / 255,
                self.a / 255)

    def get_rgba(self):
        return 

    def set_red(self, red):
        self._red = int(min(max(red, 0), 255))

    def set_green(self, green):
        self._green = int(min(max(green, 0), 255))

    def set_blue(self, blue):
        self._blue = int(min(max(blue, 0), 255))

    def set_alpha(self, alpha):
        self._alpha = int(min(max(alpha, 0), 255))

    def set_tuple(self, red, green, blue, alpha):
        self.r, self.g, self.b, self.a = red, green, blue, alpha

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


    # Properties (fold)
    red = r = property(get_red, set_red)
    green = g = property(get_green, set_green)
    blue = b = property(get_blue, set_blue)
    alpha = a = property(get_alpha, set_alpha)
    tuple = property(get_tuple, set_tuple)
    float = property(get_float, set_float)

    
def hex_to_float(hex):
    return Color.from_hex(hex).float

def hex_to_int(hex):
    return Color.from_hex(hex).tuple

# Colors (fold)
red = Color(164, 0, 0)
brown = Color(143, 89, 2)
orange = Color(206, 92, 0)
yellow = Color(196, 160, 0)
green = Color(78, 154, 6)
blue = Color(32, 74, 135)
purple = Color(92, 53, 102)
black = Color(0, 0, 0)
dark = Color(46, 52, 54)
gray = Color(85, 87, 83)
light = Color(255, 250, 240)
white = Color(255, 255, 255)

colors = {
        'red': red,
        'brown': brown,
        'orange': orange,
        'yellow': yellow,
        'green': green,
        'blue': blue,
        'purple': purple,
        'black': black,
        'gray': gray,
        'white': white }

rainbow_cycle = red, orange, yellow, green, blue, purple, brown


# Drawing utilities

def draw_line(
        vertices, color=green,
        batch=None, group=None, usage='static'):
    """
    Draw a line that passes through all the given coordinates.
    
    Parameters
    ----------
    vertices: [vector-like, ...]
        Where to draw the line.  Vertices are expected as a list of vector-like 
        objects.  This includes vecrec.Vector and 2-tuples.  3D coordinates are 
        not supported by this function.

    color: glooey.drawing.Color
        What color to make the line.
    """

    gl_vertices = ()

    for head, tail in more_itertools.pairwise(vertices):
        gl_vertices += head.tuple
        gl_vertices += tail.tuple

    num_gl_vertices = len(gl_vertices) // 2

    # Note that GL_LINE_STRIP doesn't work right in pyglet.  If a single batch 
    # has two GL_LINE_STRIPS, they will be drawn connected (unless a particular 
    # "fencing" extension happens to be installed).  With GL_TRIANGLE_STRIP and 
    # GL_QUAD_STRIP this problem can be worked around by duplicating the first 
    # coordinate in each list, but this trick doesn't work for GL_LINE_STRIP.  
    # Instead we have to use GL_LINES, which is still reasonably performant.

    return _make_vertex_list(
            batch, group, num_gl_vertices, GL_LINES,
            ('v2f/' + usage, gl_vertices),
            ('c4B', color.tuple * num_gl_vertices))

def draw_circle(
        center, radius,
        color=green, num_vertices=100,
        batch=None, group=None, usage='dynamic'):

    vertices = ()

    for iteration in range(num_vertices + 1):
        radians = math.pi * iteration / num_vertices
        if iteration % 2: radians *= -1

        vertex = center + radius * Vector.from_radians(radians)
        vertices += vertex.tuple

    vertices = vertices[0:2] + vertices + vertices[-2:]

    return _make_vertex_list(
            batch, group, num_vertices + 3, GL_TRIANGLE_STRIP,
            ('v2f/' + usage, vertices),
            ('c4B', color.tuple * (num_vertices + 3)))

def draw_rectangle(
        rect, color=green,
        batch=None, group=None, usage='static'):
    
    vertices = (
            rect.bottom_left.tuple +
            rect.bottom_right.tuple +
            rect.top_right.tuple +
            rect.top_left.tuple
    )

    return _make_vertex_list(
            batch, group, 4, GL_QUADS,
            ('v2f/' + usage, vertices),
            ('c4B', color.tuple * 4))

def draw_image(
        rect, image, tex_coords=None,
        blend_src=GL_SRC_ALPHA,
        blend_dest=GL_ONE_MINUS_SRC_ALPHA,
        batch=None, group=None, usage='static'):

    # This method is very similar in spirit to Sprite.  The difference is that 
    # sprites are meant to be dynamic; they're objects that can be continually 
    # interacted with and updated.  This function is for images that are more 
    # static; they may be deleted, but they can't be moved around.  Abandoning 
    # this flexibility allows this function to support more flexibility in how 
    # the image is drawn and to have a simpler interface.  Also, there seems to 
    # be a bug in the way sprites interpret x and y coords for rotated images.

    texture = image.get_texture()
    group = pyglet.sprite.SpriteGroup(
            texture, blend_src, blend_dest, parent=group)

    vertices = (
            rect.bottom_left.tuple +
            rect.bottom_right.tuple +
            rect.top_right.tuple +
            rect.top_left.tuple
    )

    if tex_coords is None:
        uvw = texture.tex_coords
        tex_coords = uvw[0:2] + uvw[3:5] + uvw[6:8] + uvw[9:11]

    return _make_vertex_list(
            batch, group, 4, GL_QUADS,
            ('v2f/' + usage, vertices),
            ('t2f', tex_coords))

def draw_frame(
        rect, edge_image, edge_orientation,
        corner_image=None, corner_orientation=None,
        batch=None, group=None, usage='dynamic'):

    if corner_image is None:
        edges = _draw_edges(
                rect, edge_image, edge_orientation,
                batch, group, usage)
        corners = ()

    else:
        edge_group = pyglet.graphics.OrderedGroup(0, parent=group)
        corner_group = pyglet.graphics.OrderedGroup(1, parent=group)
        
        edges = _draw_edges(
                rect, edge_image, edge_orientation,
                batch, edge_group, usage)
        corners = _draw_corners(
                rect, corner_image, corner_orientation,
                batch, corner_group, usage)

    return edges, corners

def draw_tiled_image(
        rect, image, horizontal=False, vertical=False,
        batch=None, group=None, usage='dynamic'):

    if not horizontal and not vertical:
        raise ValueError("Must specify either horizontal or vertical tiling.")

    texture = image.get_texture()
    group = pyglet.graphics.TextureGroup(texture, parent=group)

    # Figure out which texture coordinates are bound to which vertices.  This 
    # is not always an intuitive mapping, because textures can be rotated by 
    # changing which texture coordinates are bound to which vertices.  The 
    # in-line diagram shows which vertex is represent by each variable.

    a = Vector(*texture.tex_coords[0:2])     #   D +---+ C
    b = Vector(*texture.tex_coords[3:5])     #     |   |
    c = Vector(*texture.tex_coords[6:8])     #     |   |
    d = Vector(*texture.tex_coords[9:11])    #   A +---+ B

    # The given image must have a power-of-two size in each dimension that's 
    # being tiled.  This is because OpenGL internally requires that textures 
    # have power-of-two dimensions.  When pyglet loads an image that doesn't 
    # have the right dimensions, it creates a properly dimensioned texture big 
    # enough to hold the image and sets texture coordinates to indicate where 
    # in that texture the actual image is.  This information is used to hide 
    # the extra space.
    #
    # However, tiling the image requires using the whole texture in the 
    # dimension being tiled.  If the given image doesn't have a power-of-two 
    # size in that dimension, this would mean rendering the extra space.

    if horizontal:
        assert _is_power_of_two(image.width)
        b += (b - a).get_scaled(rect.width / image.width)
        c += (c - d).get_scaled(rect.width / image.width)

    if vertical:
        assert _is_power_of_two(image.height)
        c += (c - b).get_scaled(rect.height / image.height)
        d += (d - a).get_scaled(rect.height / image.height)

    tex_coords = a.tuple + b.tuple + c.tuple + d.tuple

    return draw_image(
            rect, texture, tex_coords,
            batch=batch, group=group, usage=usage)

    #x1, x2 = rect.left, rect.right
    #y1, y2 = rect.bottom, rect.top

    #vertices   = x1, y1,   x2, y1,   x2, y2,   x1, y2
    #tex_coords = a.tuple + b.tuple + c.tuple + d.tuple

    #return _make_vertex_list(
    #        batch, group, 4, GL_QUADS,
    #        ('v2f/' + usage, vertices),
    #        ('t2f', tex_coords))

def draw_pretty_line(
        start, end, stroke, color=green,
        batch=None, group=None, usage='static'):

    buffer, origin = _line_to_array(start, end, stroke)
    canvas = ones(buffer.shape + (4,), dtype='uint8')

    canvas[:,:,0] *= color.red
    canvas[:,:,1] *= color.green
    canvas[:,:,2] *= color.blue
    canvas[:,:,3] = 255 * buffer
    
    height, width = canvas.shape[0:2]
    data, stride = canvas.tostring(), canvas.strides[0]
    image = pyglet.image.ImageData(width, height, 'RGBA', data, stride) 

    return pyglet.sprite.Sprite(
            image, x=origin.x, y=origin.y,
            batch=batch, group=group, usage=usage)

def draw_donut(
        cx, cy, r1, r2,
        color=green, num_vertices=100,
        batch=None, group=None, usage='dynamic'):
    
    vertices = ()
    n = num_vertices

    for i in range(n+2):
        r = r1 if i % 2 else r2
        x = cx + r * math.cos(2 * math.pi * i / n)
        y = cy + r * math.sin(2 * math.pi * i / n)
        vertices += (x, y)

    vertices = vertices[0:2] + vertices + vertices[-2:]

    if batch is None:
        return pyglet.graphics.vertex_list(
                num_vertices + 3,
                ('v2f/%' % usage, vertices),
                ('c4B', color.tuple * (num_vertices + 4)))
    else:
        return batch.add(
                num_vertices + 4, GL_TRIANGLE_STRIP, group,
                ('v2f', vertices),
                ('c4B', color.tuple * (num_vertices + 4)))


def path_to_array(path):
    from matplotlib.pyplot import imread
    buffer = 255 * imread(path)
    buffer = buffer.astype('uint8')
    return buffer

def array_to_texture(bin, buffer):
    width, height = buffer.shape[0:2]
    data, stride = buffer.tostring(), -buffer.strides[0]
    image = pyglet.image.ImageData(width, height, 'RGBA', data, stride) 
    return bin.add(image)


def _make_vertex_list(batch, group, count, mode, *data):
    if batch is None:
        return _BoundVertexList(group, count, mode, *data)
    else:
        return batch.add(count, mode, group, *data)

def _draw_edges(
        rect, image, orientation,
        batch=None, group=None, usage='dynamic'):

    rotations = {'left': 0, 'top': 90, 'right': 180, 'bottom': 270}

    # Make rotated views of the edge textures.

    def orient_edge(desired_orientation):                           # (no fold)
        starting_rot = rotations[orientation]
        desired_rot = rotations[desired_orientation]
        return image.get_texture().get_transform(
                rotate=desired_rot-starting_rot)

    top_edge = orient_edge('top')
    bottom_edge = orient_edge('bottom')
    left_edge = orient_edge('left')
    right_edge = orient_edge('right')

    # Make a rectangle for each edge of the frame.

    top_rect = Rect.from_size(rect.width, top_edge.height)
    top_rect.top_left = rect.top_left

    bottom_rect = Rect.from_size(rect.width, bottom_edge.height)
    bottom_rect.bottom_left = rect.bottom_left

    left_rect = Rect.from_size(left_edge.width, rect.height)
    left_rect.top_left = rect.top_left

    right_rect = Rect.from_size(right_edge.width, rect.height)
    right_rect.top_right = rect.top_right

    # Draw each edge of the frame.

    params = dict(batch=batch, group=group, usage=usage)
    vertex_lists = (
            draw_tiled_image(top_rect, top_edge, horizontal=True, **params),
            draw_tiled_image(bottom_rect, bottom_edge, horizontal=True, **params),
            draw_tiled_image(left_rect, left_edge, vertical=True, **params),
            draw_tiled_image(right_rect, right_edge, vertical=True, **params),
    )
    return vertex_lists

def _draw_corners(
        rect, image, orientation,
        batch=None, group=None, usage='dynamic'):

    rotations = {
            'top left': 0,
            'top right': 90,
            'bottom right': 180,
            'bottom left': 270
    }

    if orientation not in rotations:
        raise ValueError("Unknown corner: " + orientation)
    if image.width != image.height:
        raise ValueError("Corner images must be square, not {}x{}.".format(image.width, image.height))

    # Make rotated views of the corner textures.

    def orient_corner(desired_orientation):                         # (no fold)
        starting_rot = rotations[orientation]
        desired_rot = rotations[desired_orientation]
        return image.get_texture().get_transform(
                rotate=desired_rot-starting_rot)

    bottom_left_corner = orient_corner('bottom left')
    bottom_right_corner = orient_corner('bottom right')
    top_left_corner = orient_corner('top left')
    top_right_corner = orient_corner('top right')

    # Make a rectangle for each corner.

    top_left_rect = Rect.from_pyglet_image(top_left_corner)
    top_left_rect.top_left = rect.top_left

    top_right_rect = Rect.from_pyglet_image(top_right_corner)
    top_right_rect.top_right = rect.top_right

    bottom_left_rect = Rect.from_pyglet_image(bottom_left_corner)
    bottom_left_rect.bottom_left = rect.bottom_left

    bottom_right_rect = Rect.from_pyglet_image(bottom_right_corner)
    bottom_right_rect.bottom_right = rect.bottom_right

    # Draw each of the corners.

    params = dict(batch=batch, group=group, usage=usage)
    vertex_lists = (
            draw_image(top_left_rect, top_left_corner, **params),
            draw_image(top_right_rect, top_right_corner, **params),
            draw_image(bottom_left_rect, bottom_left_corner, **params),
            draw_image(bottom_right_rect, bottom_right_corner, **params),
    )
    return vertex_lists

def _line_to_array(start, end, stroke):
    direction = end - start
    offset = stroke * direction.orthonormal

    start_plus = start + offset
    start_minus = start - offset
    end_plus = end + offset
    end_minus = end - offset
    
    # Create the canvas.
    # Don't need the canvas, just need the width and height.
    box = Rect.from_points(
            start_plus, start_minus, end_plus, end_minus)

    origin = box.top_left

    buffer = np.empty(box.size_as_int)

    # Draw an anti-aliased line.
    pixels_below = _fill_below(box, start - offset - origin, end - offset - origin)
    pixels_above = _fill_below(box, start + offset - origin, end + offset - origin)

    pixels_right = _fill_below(box, start - offset - origin, start + offset - origin)
    pixels_left  = _fill_below(box, end - offset - origin, end + offset - origin)

    return abs(pixels_below - pixels_above) * abs(pixels_left - pixels_right), origin

def _fill_below(box, start, end):
    width, height = box.size_as_int
    size = arange(width), arange(height)
    x, y = meshgrid(*size)

    left, right = x, x + 1
    top, bottom = y, y + 1

    if end.x == start.x:
        return clip(x - end.x, 0, 1)

    if end.y == start.y:
        return clip(y - end.y, 0, 1)

    f = lambda x: slope * x + intercept
    g = lambda y: (y - intercept) / slope

    slope = (end.y - start.y) / (end.x - start.x)
    intercept = end.y - slope * end.x

    crossings = clip(g(top), left, right), clip(g(bottom), left, right)
    enter, exit = minimum(*crossings), maximum(*crossings)

    enter_area = (enter - left) * clip(bottom - f(enter), 0, 1)
    exit_area = (right - exit) * clip(bottom - f(exit), 0, 1)
    line_area =                                     \
            - slope * (exit**2 - enter**2) / 2      \
            + (bottom - intercept) * (exit - enter)

    return enter_area + exit_area + line_area

def _is_power_of_two(x):
    # Like most binary tricks, this is best explained with examples.  First, 
    # consider a case where x is a power of two, e.g. x = 16:
    #
    # x           = 16 = 10000
    # x - 1       = 15 = 01111
    # x & (x - 1) =  0 = 00000
    #
    # Now consider a case where x is not a power of two, e.g. x = 17
    #
    # x           = 17 = 10001
    # x - 1       = 16 = 10000
    # x & (x - 1) = 16 = 10000

    return x > 0 and x & (x - 1) == 0


class _BoundVertexList:

    def __init__(self, group, count, mode, *data):
        self.vertex_list = pyglet.graphics.vertex_list(count, *data)
        self.mode = mode
        self.group = group

    def draw(self):
        self.group.set_state()
        self.vertex_list.draw(self.mode)
        self.group.unset_state()

    def delete(self):
        self.vertex_list.delete()



# Clipping mask utilities

class StencilGroup (Group):

    def __init__(self, parent=None):
        Group.__init__(self, parent)

    def set_state(self):
        from pyglet.gl import GL_STENCIL_TEST
        from pyglet.gl import GL_STENCIL_BUFFER_BIT
        from pyglet.gl import GL_DEPTH_BUFFER_BIT

        pyglet.gl.glEnable(GL_STENCIL_TEST)
        pyglet.gl.glClear(GL_DEPTH_BUFFER_BIT)
        pyglet.gl.glClear(GL_STENCIL_BUFFER_BIT)

    def unset_state(self):
        from pyglet.gl import GL_STENCIL_TEST
        pyglet.gl.glDisable(GL_STENCIL_TEST)


class StencilMask (Group):

    def __init__(self, parent=None):
        Group.__init__(self, parent)

    def set_state(self):
        from pyglet.gl import GL_FALSE, GL_NEVER
        from pyglet.gl import GL_REPLACE, GL_KEEP

        pyglet.gl.glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        pyglet.gl.glDepthMask(GL_FALSE)
        pyglet.gl.glStencilFunc(GL_NEVER, 1, 0xFF)
        pyglet.gl.glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)

        pyglet.gl.glStencilMask(0xFF)

    def unset_state(self):
        from pyglet.gl import GL_TRUE
        pyglet.gl.glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        pyglet.gl.glDepthMask(GL_TRUE);


class WhereStencilIs (Group):

    def __init__(self, parent=None):
        Group.__init__(self, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00)
        pyglet.gl.glStencilFunc(GL_EQUAL, 1, 0xFF)

    def unset_state(self):
        pass


class WhereStencilIsnt (Group):

    def __init__(self, parent=None):
        Group.__init__(self, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00);
        pyglet.gl.glStencilFunc(GL_EQUAL, 0, 0xFF)

    def unset_state(self):
        pass



