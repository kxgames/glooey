import math
import pyglet
import more_itertools
import vecrec

from pprint import pprint
from vecrec import Vector, Rect
from pyglet.gl import *
from pyglet.graphics import Group, OrderedGroup
from .helpers import *

# Color utilities

class Color (object):

    # Right now, the color class's internal representation is integers.  I 
    # don't know if this is a good thing, because integers aren't as expressive 
    # as floats.  This surprised me when I tried to use __truediv__ to 
    # implement get_float().  It didn't work because the RGBA values got 
    # converted to ints before being returned.

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

colors = {  # (no fold)
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

class Artist:

    def __init__(self, batch, group, count, mode, *data):
        self._batch = batch
        self._group = group
        self._count = count
        self._mode = mode
        self._vertex_list = batch.add(
                count, mode, self._group_factory(group), *data)

    def get_batch(self):
        return self._batch

    def set_batch(self, new_batch):
        if self._batch is not new_batch:
            self._batch.migrate(
                    self._vertex_list, self._mode, self._group, new_batch)

    batch = property(get_batch, set_batch)

    def get_group(self):
        return self._group

    def set_group(self, new_group):
        if self._parent_group is not new_group:
            self._group = new_group
            self._update_group()

    group = property(get_group, set_group)

    def get_count(self):
        return self._count

    count = property(get_count)

    def get_mode(self):
        return self._mode

    mode = property(get_mode)

    def get_vertex_list(self):
        return self._vertex_list

    vertex_list = property(get_vertex_list)

    def delete(self):
        self._vertex_list.delete()

    def _group_factory(self, parent):
        return parent

    def _update_group(self):
        self._batch.migrate(
                self._vertex_list,
                self._mode,
                self._group_factory(self._group),
                self._batch,
        )


class Rectangle(Artist):

    def __init__(self, rect, color=green,
            batch=None, group=None, usage='static'):

        data = 'v2f/' + usage, 'c4B/' + usage
        super().__init__(batch, group, 4, GL_QUADS, *data)
        self.rect = rect
        self.color = color

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        self._rect = new_rect
        self.vertex_list.vertices = (
                new_rect.bottom_left.tuple +
                new_rect.bottom_right.tuple +
                new_rect.top_right.tuple +
                new_rect.top_left.tuple
        )

    rect = property(get_rect, set_rect)

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        self.vertex_list.colors = 4 * new_color.tuple

    color = property(get_color, set_color)


class Tile(Artist):

    def __init__(self, rect, image, htile=True, vtile=True,
            blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA,
            batch=None, group=None, usage='static'):

        self._rect = rect
        self._image = image
        self._htile = htile
        self._vtile = vtile
        self._blend_src = blend_src
        self._blend_dest = blend_dest

        data = 'v2f/' + usage, 't2f/' + usage
        super().__init__(batch, group, 4, GL_QUADS, *data)
        self._update_vertex_list()

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        self._rect = new_rect
        self._update_vertex_list()

    rect = property(get_rect, set_rect)

    def get_image(self):
        return self._image

    def set_image(self, new_image, htile=None, vtile=None):
        self._image = new_image
        if htile is not None: self._htile = htile
        if vtile is not None: self._vtile = vtile
        self._update_group()
        self._update_vertex_list()

    image = property(get_image, set_image)

    def get_htile(self):
        return self._htile

    def set_htile(self, new_htile):
        self._htile = new_htile
        self._update_vertex_list()

    htile = property(get_htile, set_htile)

    def get_vtile(self):
        return self._vtile

    def set_vtile(self, new_vtile):
        self._vtile = new_vtile
        self._update_vertex_list()

    vtile = property(get_vtile, set_vtile)

    def get_blend_src(self):
        return self._blend_src

    def set_blend_src(self, new_blend_src):
        self._blend_src = new_blend_src
        self._update_group()

    blend_src = property(get_blend_src, set_blend_src)

    def get_blend_dest(self):
        return self._blend_dest

    def set_blend_dest(self, new_blend_dest):
        self._blend_dest = new_blend_dest
        self._update_group()

    blend_dest = property(get_blend_dest, set_blend_dest)

    def _group_factory(self, parent):
        return pyglet.sprite.SpriteGroup(
                self._image.get_texture(),
                self._blend_src,
                self._blend_dest,
                parent=parent,
        )

    def _update_vertex_list(self):
        texture = self._image.get_texture()

        # Figure out which texture coordinates are bound to which vertices.  
        # This is not always an intuitive mapping, because textures can be 
        # rotated by changing which texture coordinates are bound to which 
        # vertices.  The in-line diagram shows which vertex is represented by 
        # each variable in the case that the image hasn't been rotated.

        a = Vector(*texture.tex_coords[0:2])     #   D┌───┐C
        b = Vector(*texture.tex_coords[3:5])     #    │   │
        c = Vector(*texture.tex_coords[6:8])     #    │   │
        d = Vector(*texture.tex_coords[9:11])    #   A└───┘B

        # The given image must have a power-of-two size in each dimension being 
        # tiled.  This is because OpenGL internally requires that textures have 
        # power-of-two dimensions.  When pyglet loads an image that doesn't 
        # have the right dimensions, it creates a properly dimensioned texture 
        # big enough to hold the image, sets texture coordinates to indicate 
        # where in that texture the actual image is, and uses that information 
        # to hide the extra space.
        #
        # However, tiling the image requires using the whole texture in each  
        # dimension being tiled.  If the given image doesn't have a power-of- 
        # two size in that dimension, this extra space would be rendered.

        w, h = 1, 1

        if self._htile:
            if not _is_power_of_two(self._image.width):
                raise UsageError("image is {self._image.width} px wide; can only tile images with power-of-two dimensions")
            w = self._rect.width / self._image.width
        if self._vtile:
            if not _is_power_of_two(self._image.height):
                raise UsageError("image is {self._image.height} px tall; can only tile images with power-of-two dimensions")
            h = self._rect.height / self._image.height

        A = a
        B = a + (b - a).get_scaled(w)
        C = a + (c - d).get_scaled(w) + (c - b).get_scaled(h)
        D = a                         + (d - a).get_scaled(h)

        self._vertex_list.tex_coords = A.tuple + B.tuple + C.tuple + D.tuple
        self._vertex_list.vertices = (
                self._rect.bottom_left.tuple +
                self._rect.bottom_right.tuple +
                self._rect.top_right.tuple +
                self._rect.top_left.tuple
        )



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
        gl_vertices += vecrec.cast_anything_to_vector(head).tuple
        gl_vertices += vecrec.cast_anything_to_vector(tail).tuple

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

def draw_convex_polygon(
        vertices, color=green,
        batch=None, group=None, usage='static'):
    """
    Draw a filled-in polygon with the given vertices.  The polygon must be 
    convex, otherwise the algorithm used to convert it to triangles will not 
    work properly.
    """

    assert len(vertices) > 2

    # If you use this function to render more than one polygon per batch, they 
    # will end up all connected.  I haven't figured out how to solve this 
    # problem yet.

    gl_vertices = sum((
        vecrec.cast_anything_to_vector(vertex).tuple
        for vertex in vertices), ())
    num_gl_vertices = len(gl_vertices) // 2

    return _make_vertex_list(
            batch, group, num_gl_vertices, GL_TRIANGLE_FAN,
            ('v2f/' + usage, gl_vertices),
            ('c4B', color.tuple * num_gl_vertices))

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
    # in-line diagram shows which vertex is represented by each variable.

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


class BoundVertexList:

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
    """
    Return true if ``x`` is a power of two, e.g. 1, 2, 4, 8, etc.
    """

    # Like most binary tricks, this is best explained with examples.  First, 
    # consider a case where x is a power of two, e.g. x = 16:
    #
    # x           = 16 = 10000
    # x - 1       = 15 = 01111
    # x & (x - 1) =  0 = 00000 == 0
    #
    # Now consider a case where x is not a power of two, e.g. x = 17
    #
    # x           = 17 = 10001
    # x - 1       = 16 = 10000
    # x & (x - 1) = 16 = 10000 != 0

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


class StencilMask (OrderedGroup):

    def __init__(self, parent=None, order=0):
        super().__init__(order, parent)

    def set_state(self):
        from pyglet.gl import GL_FALSE, GL_NEVER
        from pyglet.gl import GL_REPLACE, GL_KEEP

        # Disable writing the to color or depth buffers.
        pyglet.gl.glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        pyglet.gl.glDepthMask(GL_FALSE)

        pyglet.gl.glStencilFunc(GL_NEVER, 1, 0xFF)
        pyglet.gl.glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)
        pyglet.gl.glStencilMask(0xFF)

    def unset_state(self):
        from pyglet.gl import GL_TRUE
        pyglet.gl.glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        pyglet.gl.glDepthMask(GL_TRUE);


class WhereStencilIs (OrderedGroup):

    def __init__(self, parent=None, order=1):
        super().__init__(order, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00)
        pyglet.gl.glStencilFunc(GL_EQUAL, 1, 0xFF)

    def unset_state(self):
        pass


class WhereStencilIsnt (OrderedGroup):

    def __init__(self, parent=None, order=1):
        super().__init__(order, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00);
        pyglet.gl.glStencilFunc(GL_EQUAL, 0, 0xFF)

    def unset_state(self):
        pass



# Rectangle placement utilities

class Grid:

    def __init__(self, *, bounding_rect=None, min_cell_rects={},
            num_rows=0, num_cols=0, padding=0, row_heights={}, col_widths={},
            default_row_height='expand', default_col_width='expand'):

        # Attributes that the user can set to affect the shape of the grid.  
        self._bounding_rect = bounding_rect or Rect.null()
        self._min_cell_rects = min_cell_rects
        self._requested_num_rows = num_rows
        self._requested_num_cols = num_cols
        self._padding = padding
        self._requested_row_heights = row_heights
        self._requested_col_widths = col_widths
        self._default_row_height = default_row_height
        self._default_col_width = default_col_width

        # Read-only attributes that reflect the current state of the grid.
        self._num_rows = 0
        self._num_cols = 0
        self._max_cell_heights = {}
        self._max_cell_widths = {}
        self._fixed_rows = set()
        self._expandable_rows = set()
        self._fixed_cols = set()
        self._expandable_cols = set()
        self._fixed_row_heights = {}
        self._fixed_col_widths = {}
        self._min_expandable_row_heights = {}
        self._min_expandable_col_widths = {}
        self._min_height = 0
        self._min_width = 0
        self._row_heights = {}
        self._col_widths = {}
        self._cell_rects = {}

        # Attributes that manage the cache.
        self._is_shape_stale = True
        self._is_claim_stale = True
        self._are_cells_stale = True

    def make_claim(self, min_cell_rects=None):
        if min_cell_rects is not None:
            self.min_cell_rects = min_cell_rects

        self._update_claim()

        return self._min_width, self._min_height

    def make_cells(self, bounding_rect=None):
        if bounding_rect is not None:
            self.bounding_rect = bounding_rect

        self._update_cells()

        return self._cell_rects

    def get_min_width(self):
        return self._min_width

    min_width = property(get_min_width)

    def get_min_height(self):
        return self._min_height

    min_height = property(get_min_height)

    def get_min_bounding_rect(self):
        return Rect.from_size(self._min_width, self._min_height)

    min_bounding_rect = property(get_min_bounding_rect)

    def get_cell_rects(self):
        return self._cell_rects

    cell_rects = property(get_cell_rects)

    def get_bounding_rect(self):
        return self._bounding_rect

    def set_bounding_rect(self, new_rect):
        if self._bounding_rect != new_rect:
            self._bounding_rect = new_rect
            self._invalidate_cells()

    bounding_rect = property(get_bounding_rect, set_bounding_rect)

    def get_min_cell_rect(self, i, j):
        return self._min_cell_rects[i,j]

    def set_min_cell_rect(self, i, j, new_rect):
        if (i,j) not in self._min_cell_rects or \
                self._min_cell_rects[i,j] != new_rect:
            self._min_cell_rects[i,j] = new_rect
            self._invalidate_shape()

    def get_min_cell_rects(self):
        return self._min_cell_rects

    def set_min_cell_rects(self, new_rects):
        if self._min_cell_rects != new_rects:
            self._min_cell_rects = new_rects
            self._invalidate_shape()

    min_cell_rects = property(get_min_cell_rects, set_min_cell_rects)

    def unset_min_cell_rect(self, i, j):
        if (i,j) in self._min_cell_rects:
            del self._min_cell_rects[i,j]
            self._invalidate_shape()

    def unset_min_cell_rects(self):
        if self._min_cell_rects:
            self._min_cell_rects = {}
            self._invalidate_shape()

    def get_num_rows(self):
        return self._num_rows

    def set_num_rows(self, new_num):
        self._requested_num_rows = new_num
        self._invalidate_shape()

    num_rows = property(get_num_rows, set_num_rows)

    def get_num_cols(self):
        return self._num_cols

    def set_num_cols(self, new_num):
        self._requested_num_cols = new_num
        self._invalidate_shape()

    num_cols = property(get_num_cols, set_num_cols)

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding):
        self._padding = new_padding
        self._invalidate_claim()

    padding = property(get_padding, set_padding)

    def get_row_height(self, i):
        return self._row_heights[i]

    def set_row_height(self, i, new_height):
        self._requested_row_heights[i] = new_height
        self._invalidate_claim()

    def get_row_heights(self):
        return self._row_heights

    def set_row_heights(self, new_heights):
        self._requested_row_heights = new_heights
        self._invalidate_claim()

    row_heights = property(get_row_heights, set_row_heights)

    def get_col_width(self, j):
        return self._col_widths[j]

    def set_col_width(self, j, new_width):
        self._requested_col_widths[j] = new_width
        self._invalidate_claim()

    def get_col_widths(self):
        return self._col_widths

    def set_col_widths(self, new_widths):
        self._requested_col_widths = new_widths
        self._invalidate_claim()

    col_widths = property(get_col_widths, set_col_widths)

    def unset_row_height(self, i):
        del self._requested_row_heights[i]
        self._invalidate_claim()

    def unset_col_width(self, j):
        del self._requested_col_widths[j]
        self._invalidate_claim()

    def get_default_row_height(self):
        return self._default_row_height

    def set_default_row_height(self, new_height):
        self._default_row_height = new_height
        self._invalidate_claim()

    default_row_height = property(
            get_default_row_height, set_default_row_height)

    def get_default_col_width(self):
        return self._default_col_width

    def set_default_col_width(self, new_width):
        self._default_col_width = new_width
        self._invalidate_claim()

    default_col_width = property(
            get_default_col_width, set_default_col_width)

    def get_requested_num_rows(self):
        return self._requested_num_rows

    requested_num_rows = property(get_requested_num_rows)

    def get_requested_num_cols(self):
        return self._requested_num_cols

    requested_num_cols = property(get_requested_num_cols)

    def get_requested_row_height(self, i):
        return self._requested_row_heights[i]

    def get_requested_row_heights(self):
        return self._requested_row_heights

    requested_row_heights = property(get_requested_row_heights)

    def get_requested_col_width(self, i):
        return self._requested_col_widths[i]

    def get_requested_col_widths(self):
        return self._requested_col_widths

    requested_col_widths = property(get_requested_col_widths)

    def _invalidate_shape(self):
        self._is_shape_stale = True
        self._invalidate_claim()

    def _invalidate_claim(self):
        self._is_claim_stale = True
        self._invalidate_cells()

    def _invalidate_cells(self):
        self._are_cells_stale = True

    def _update_shape(self):
        if self._is_shape_stale:
            self._find_num_rows()
            self._find_num_cols()
            self._find_max_cell_dimensions()
            self.is_shape_stale = False

    def _update_claim(self):
        if self._is_claim_stale:
            self._update_shape()
            self._find_which_rows_expand()
            self._find_which_cols_expand()
            self._find_fixed_row_heights()
            self._find_fixed_col_widths()
            self._find_min_expandable_row_heights()
            self._find_min_expandable_col_widths()
            self._find_min_height()
            self._find_min_width()
            self._is_claim_stale = False

    def _update_cells(self):
        if self._are_cells_stale:
            self._update_claim()

            if self._bounding_rect.width < self._min_width:
                raise UsageError("grid cannot fit in {0[0]}x{0[1]}, need to be at least {1} px wide.".format(self._bounding_rect.size, self._min_width))
            if self._bounding_rect.height < self._min_height:
                raise UsageError("grid cannot fit in {0[0]}x{0[1]}, need to be at least {1} px tall.".format(self._bounding_rect.size, self._min_height))

            self._find_row_heights()
            self._find_col_widths()
            self._find_cell_rects()
            self._are_cells_stale = False

    def _find_num_rows(self):
        min_num_rows = 0
        for i,j in self._min_cell_rects:
            min_num_rows = max(i+1, min_num_rows)

        if self._requested_num_rows:
            self._num_rows = self._requested_num_rows
        else:
            self._num_rows = min_num_rows

        if self._num_rows < min_num_rows:
            raise UsageError("not enough rows requested")

    def _find_num_cols(self):
        min_num_cols = 0
        for i,j in self._min_cell_rects:
            min_num_cols = max(j+1, min_num_cols)

        if self._requested_num_cols:
            self._num_cols = self._requested_num_cols
        else:
            self._num_cols = min_num_cols

        if self._num_cols < min_num_cols:
            raise UsageError("not enough columns requested")

    def _find_max_cell_dimensions(self):
        self._max_cell_heights = {}
        self._max_cell_widths = {}

        for i,j in self._min_cell_rects:
            # Use -math.inf so that negative cell sizes can be used.
            self._max_cell_heights[i] = max(
                    self._min_cell_rects[i,j].height,
                    self._max_cell_heights.get(i, -math.inf))
            self._max_cell_widths[j] = max(
                    self._min_cell_rects[i,j].width,
                    self._max_cell_widths.get(j, -math.inf))

    def _find_which_rows_expand(self):
        self._fixed_rows = set()
        self._expandable_rows = set()

        for i in range(self._num_rows):
            size_request = self._get_requested_row_height(i)

            if isinstance(size_request, int):
                self._fixed_rows.add(i)
            elif size_request == 'expand':
                self._expandable_rows.add(i)
            else:
                raise UsageError("illegal row height: {}".format(repr(size_request)))

        self._num_fixed_rows = len(self._fixed_rows)
        self._num_expandable_rows = len(self._expandable_rows)

    def _find_which_cols_expand(self):
        self._fixed_cols = set()
        self._expandable_cols = set()

        for j in range(self._num_cols):
            size_request = self._get_requested_col_width(j)

            if isinstance(size_request, int):
                self._fixed_cols.add(j)
            elif size_request == 'expand':
                self._expandable_cols.add(j)
            else:
                raise UsageError("illegal col width: {}".format(repr(size_request)))

        self._num_fixed_cols = len(self._fixed_cols)
        self._num_expandable_cols = len(self._expandable_cols)

    def _find_fixed_row_heights(self):
        self._fixed_row_heights = {}
        for i in self._fixed_rows:
            # Use -math.inf so that negative cell sizes can be used.
            self._fixed_row_heights[i] = max(
                    self._get_requested_row_height(i),
                    self._max_cell_heights.get(i, -math.inf))

    def _find_fixed_col_widths(self):
        self._fixed_col_widths = {}
        for j in self._fixed_cols:
            # Use -math.inf so that negative cell sizes can be used.
            self._fixed_col_widths[j] = max(
                    self._get_requested_col_width(j),
                    self._max_cell_widths.get(j, -math.inf))

    def _find_min_expandable_row_heights(self):
        self._min_expandable_row_heights = {}
        for i in self._expandable_rows:
            self._min_expandable_row_heights[i] = \
                    self._max_cell_heights.get(i, 0)

    def _find_min_expandable_col_widths(self):
        self._min_expandable_col_widths = {}
        for j in self._expandable_cols:
            self._min_expandable_col_widths[j] = \
                    self._max_cell_widths.get(j, 0)

    def _find_min_height(self):
        min_expandable_height = max(
                self._min_expandable_row_heights.values() or [0])
        self._min_height = \
                + sum(self._fixed_row_heights.values())  \
                + min_expandable_height * self._num_expandable_rows \
                + self._padding * (self._num_rows + 1)

    def _find_min_width(self):
        min_expandable_width = max(
                self._min_expandable_col_widths.values() or [0])
        self._min_width = \
                + sum(self._fixed_col_widths.values())  \
                + min_expandable_width * self._num_expandable_cols \
                + self._padding * (self._num_cols + 1)

    def _find_row_heights(self):
        self._row_heights = self._fixed_row_heights.copy()

        if self._num_expandable_rows:
            expandable_row_height = (
                    + self._bounding_rect.height
                    - sum(self._fixed_row_heights.values())
                    - self._padding * (self._num_rows + 1)
                    ) / self._num_expandable_rows

            for i in self._expandable_rows:
                self._row_heights[i] = expandable_row_height

    def _find_col_widths(self):
        self._col_widths = self._fixed_col_widths.copy()

        if self._num_expandable_cols:
            expandable_col_width = (
                    + self._bounding_rect.width
                    - sum(self._fixed_col_widths.values())
                    - self._padding * (self._num_cols + 1)
                    ) / self._num_expandable_cols

            for j in self._expandable_cols:
                self._col_widths[j] = expandable_col_width

    def _find_cell_rects(self):
        self._cell_rects = {}
        top_cursor = self._bounding_rect.top

        for i in range(self._num_rows):
            top_cursor -= self._padding
            row_height = self._row_heights[i]
            left_cursor = self._bounding_rect.left

            for j in range(self._num_cols):
                left_cursor += self._padding
                col_width = self._col_widths[j]

                self._cell_rects[i,j] = Rect.from_size(col_width, row_height)
                self._cell_rects[i,j].top_left = left_cursor, top_cursor

                left_cursor += col_width
            top_cursor -= row_height

    def _get_requested_row_height(self, i):
        return self._requested_row_heights.get(i, self._default_row_height)

    def _get_requested_col_width(self, j):
        return self._requested_col_widths.get(j, self._default_col_width)



def make_grid(rect, cells={}, num_rows=0, num_cols=0, padding=0,
        row_heights={}, col_widths={}, default_row_height='expand',
        default_col_width='expand'):
    """
    Return rectangles for each cell in the specified grid.  The rectangles are 
    returned in a dictionary where the keys are (row, col) tuples.
    """
    grid = Grid(
            bounding_rect=rect,
            min_cell_rects=cells,
            num_rows=num_rows,
            num_cols=num_cols,
            padding=padding,
            row_heights=row_heights,
            col_widths=col_widths,
            default_row_height=default_row_height,
            default_col_width=default_col_width,
    )
    return grid.make_cells()
