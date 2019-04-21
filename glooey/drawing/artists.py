#!/usr/bin/env python3

import pyglet
import autoprop
from vecrec import Vector, Rect
from collections import defaultdict
from pyglet.gl import *
from glooey.helpers import *
from glooey.drawing.grid import Grid
from glooey.drawing.color import Color

@autoprop
class Artist(HoldUpdatesMixin):

    def __init__(self, batch, group, count, mode, data, hidden=False):
        super().__init__()
        self._batch = batch
        self._group = group
        self._count = count
        self._mode = mode
        self._data = data
        self._vertex_list = None

        if batch and not hidden:
            self._create_vertex_list()
            self._update_vertex_list()

    def get_batch(self):
        return self._batch

    def set_batch(self, new_batch):
        if self._batch is not new_batch:
            if self._batch is not None:
                self._batch.migrate(
                        self._vertex_list, self._mode, self._group, new_batch)
            self._batch = new_batch

    def get_group(self):
        return self._group

    def set_group(self, new_group):
        if self._group is not new_group:
            self._group = new_group
            self._update_group()

    def get_count(self):
        return self._count

    def get_mode(self):
        return self._mode

    def get_vertex_list(self):
        return self._vertex_list

    def hide(self):
        if self._vertex_list:
            self._vertex_list.delete()
            self._vertex_list = None

    def show(self):
        if not self._vertex_list:
            self._create_vertex_list()
            self._update_vertex_list()

    def _create_vertex_list(self):
        self._vertex_list = self._batch.add(
                self._count,
                self._mode,
                self._group_factory(self._group),
                *self._data)

    def _update_vertex_list(self):
        raise NotImplementedError

    def _group_factory(self, parent):
        return parent

    @update_function
    def _update_group(self):
        if self._vertex_list is not None:
            self._batch.migrate(
                    self._vertex_list,
                    self._mode,
                    self._group_factory(self._group),
                    self._batch,
            )


@autoprop
class Rectangle(Artist):

    def __init__(self, rect=None, color='green', *,
            batch=None, group=None, usage='static', hidden=False):

        self._rect = rect or Rect.null()
        self._color = Color.from_anything(color)

        data = 'v2f/' + usage, 'c4B/' + usage
        super().__init__(batch, group, 4, GL_QUADS, data, hidden)

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        self._rect = new_rect
        self.update_rect()

    def update_rect(self):
        """
        Call this method to update the tile after you've made an in-place 
        change to its rectangle.
        """
        if self.vertex_list:
            self.vertex_list.vertices = (
                    self._rect.bottom_left.tuple +
                    self._rect.bottom_right.tuple +
                    self._rect.top_right.tuple +
                    self._rect.top_left.tuple
            )

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = Color.from_anything(new_color)
        self.update_color()

    def update_color(self):
        if self.vertex_list:
            self.vertex_list.colors = 4 * self._color.tuple

    def _update_vertex_list(self):
        self.update_rect()
        self.update_color()


@autoprop
class Outline(Artist):

    def __init__(self, rect=None, color='green', *,
            batch=None, group=None, usage='static', hidden=False):

        self._rect = rect or Rect.null()
        self._color = Color.from_anything(color)

        data = 'v2f/' + usage, 'c4B/' + usage
        super().__init__(batch, group, 8, GL_LINES, data, hidden)

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        self._rect = new_rect
        self.update_rect()

    def update_rect(self):
        """
        Call this method to update the tile after you've made an in-place 
        change to its rectangle.
        """
        if self.vertex_list:
            # Shrink the rectangle by half-a-pixel so there's no ambiguity 
            # about where the line should be drawn.  (The problem is that the 
            # widget rect is always rounded to the nearest pixel, but OpenGL 
            # doesn't seem deterministic about which side of the pixel it draws 
            # the line on.)
            rect = self._rect.get_shrunk(0.5)
            self.vertex_list.vertices = (
                    rect.bottom_left.tuple +
                    # Don't know why this offset is necessary, but without it 
                    # the bottom-right pixel doesn't get filled in...
                    (rect.bottom_right + (1,0)).tuple +
                    rect.bottom_right.tuple +
                    rect.top_right.tuple +
                    rect.top_right.tuple +
                    rect.top_left.tuple +
                    rect.top_left.tuple +
                    rect.bottom_left.tuple
            )

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = Color.from_anything(new_color)
        self.update_color()

    def update_color(self):
        if self.vertex_list:
            self.vertex_list.colors = 8 * self._color.tuple

    def _update_vertex_list(self):
        self.update_rect()
        self.update_color()


@autoprop
class Tile(Artist):

    def __init__(self, rect, image, *, htile=False, vtile=False,
            blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA,
            batch=None, group=None, usage='static', hidden=False):

        self._rect = rect
        self._image = image
        self._htile = htile
        self._vtile = vtile
        self._blend_src = blend_src
        self._blend_dest = blend_dest

        data = 'v2f/' + usage, 't2f/' + usage
        super().__init__(batch, group, 4, GL_QUADS, data, hidden)

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        if self._rect != new_rect:
            self._rect = new_rect
            self.update_rect()

    def update_rect(self):
        """
        Call this method to update the tile after you've made an in-place 
        change to its rectangle.
        """
        self._update_vertex_list()

    def get_image(self):
        return self._image

    def set_image(self, new_image, htile=None, vtile=None):
        # Don't bother redrawing everything if nothing changed.
        if self._image is new_image:
            if htile is None or self._htile == htile:
                if vtile is None or self._vtile == vtile:
                    return

        self._image = new_image
        if htile is not None: self._htile = htile
        if vtile is not None: self._vtile = vtile

        self._update_group()
        self._update_vertex_list()

    def get_htile(self):
        return self._htile

    def set_htile(self, new_htile):
        if self._htile != new_htile:
            self._htile = new_htile
            self._update_vertex_list()

    def get_vtile(self):
        return self._vtile

    def set_vtile(self, new_vtile):
        if self._vtile != new_vtile:
            self._vtile = new_vtile
            self._update_vertex_list()

    def get_blend_src(self):
        return self._blend_src

    def set_blend_src(self, new_blend_src):
        if self._blend_src != new_blend_src:
            self._blend_src = new_blend_src
            self._update_group()

    def get_blend_dest(self):
        return self._blend_dest

    def set_blend_dest(self, new_blend_dest):
        if self._blend_dest != new_blend_dest:
            self._blend_dest = new_blend_dest
            self._update_group()

    @update_function
    def _update_vertex_list(self):
        if self._vertex_list is None:
            return

        texture = self._image.get_texture()

        # Get the actual texture (not just a region of a texture) associated 
        # for this image.  This will be used to make sure that 
        try:
            underlying_texture = texture.owner
        except AttributeError:
            underlying_texture = texture

        # Figure out which texture coordinates are bound to which vertices.  
        # This is not always an intuitive mapping, because textures can be 
        # rotated by changing which texture coordinates are bound to which 
        # vertices.  The in-line diagram shows which vertex is represented by 
        # each variable in the case that the image hasn't been rotated.

        a = Vector(*texture.tex_coords[0:2])     #   D┌───┐C
        b = Vector(*texture.tex_coords[3:5])     #    │   │
        c = Vector(*texture.tex_coords[6:8])     #    │   │
        d = Vector(*texture.tex_coords[9:11])    #   A└───┘B

        # Give a really nice error message if the image can't be tiled, because 
        # the restrictions on which images can be tiled don't make sense unless 
        # you really know how OpenGL works.

        error_template = """\
image can't be tiled {} because it's {} than its underlying texture ({} px vs {} px).

The most common way to get this error is to use an image that doesn't have a 
power-of-two size (e.g. 1, 2, 4, 8, etc.) in each dimension being tiled.  
OpenGL requires that textures have power-of-two dimensions, so images with 
non-power-of-two sizes end up in textures with some unused space.  This unused 
space is usually not shown, but tiling requires showing the whole texture in 
the dimension being tiled, so the unused space would ruin the effect.

Another common way to get this error is by loading the image as an `image` 
rather than a `texture`.  Pyglet tries to be smart about packing images into 
contiguous regions of memory, and sometimes this means putting images in 
textures that are larger than they need to be.  Loading the image as a texture 
avoids this logic at the expense of less well-organized memory."""

        if self._htile:
            if self._image.width != underlying_texture.width:
                raise UsageError(error_template.format('horizontally', 'narrower', self._image.width, underlying_texture.width))
            w = self._rect.width / self._image.width
        else:
            w = a.get_distance(b)

        if self._vtile:
            if self._image.height != underlying_texture.height:
                raise UsageError(error_template.format('vertically', 'shorter', self._image.height, underlying_texture.height))
            h = self._rect.height / self._image.height
        else:
            h = a.get_distance(d)

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

    def _group_factory(self, parent):
        return pyglet.sprite.SpriteGroup(
                self._image.get_texture(),
                self._blend_src,
                self._blend_dest,
                parent=parent,
        )


@autoprop
class Background(HoldUpdatesMixin):
    """\
    Auto-tiling:
    Basically the assumption is that if we specify images for one side (e.g. 
    the top), then we will be tiling in the direction orthogonal to that side 
    (e.g. vertically for the top).
    """

    def __init__(self, *, rect=None, color=None, outline=None, image=None, 
            center=None, top=None, bottom=None, left=None, right=None, 
            top_left=None, top_right=None, bottom_left=None, bottom_right=None, 
            vtile='auto', htile='auto', batch=None, group=None, usage='static', 
            hidden=False):

        super().__init__()

        self._grid = Grid(
                num_rows=3,
                num_cols=3,
                default_row_height=0,
                default_col_width=0,
        )
        self._rect = rect
        self._color = None
        self._color_artist = None
        self._color_group = None
        self._outline = None
        self._outline_artist = None
        self._outline_group = None
        self._tile_images = {}
        self._tile_artists = {}
        self._tile_group = None
        self._htile = False
        self._vtile = False
        self._batch = batch
        self._group = group
        self._usage = usage
        self._hidden = hidden

        self._update_group()
        self.set_appearance(
                color=color,
                outline=outline,
                image=image,
                center=center,
                top=top,
                bottom=bottom,
                left=left,
                right=right,
                top_left=top_left,
                top_right=top_right,
                bottom_left=bottom_left,
                bottom_right=bottom_right,
                htile=htile,
                vtile=vtile,
        )

    @update_function
    def _update_group(self):
        self._color_group = pyglet.graphics.OrderedGroup(0, self._group)
        self._outline_group = pyglet.graphics.OrderedGroup(2, self._group)
        self._tile_group = pyglet.graphics.OrderedGroup(1, self._group)

        if self._color_artist:
            self._color_artist.group = self._color_group

        if self._outline_artist:
            self._outline_artist.group = self._outline_group

        for artist in self._tile_artists.values():
            artist.group = self._tile_group

    @update_function
    def _update_tiles(self):
        if self._hidden or self._rect is None or self._batch is None:
            return

        # Create a grid of rectangles with enough space for all the images the 
        # user gave.  Whether or not the background can tile (vertically or 
        # horizontally) affects how much space the grid takes up.

        self._grid.bounding_rect = self._rect
        self._grid.row_heights = {1: 'expand' if self._vtile else 0}
        self._grid.col_widths = {1: 'expand' if self._htile else 0}

        tile_rects = self._grid.make_cells()

        # Figure out how big the color and outline artists need to be.  
        # Normally they can just fill the whole background.  However, if the 
        # images don't tile and only take up a subset of the available space, 
        # we want the rest of the artists to use the same space.

        apparent_rect = self._grid.rect if self._tile_images else self._rect

        # Draw a colored rectangle behind everything else if the user provided 
        # a color.

        have_artist = self._color_artist is not None
        have_color = self._color is not None
        
        if have_color and have_artist:
            self._color_artist.rect = apparent_rect
            self._color_artist.color = self._color

        if have_color and not have_artist:
            self._color_artist = Rectangle(
                    rect=apparent_rect,
                    color=self._color, 
                    batch=self._batch,
                    group=self._color_group,
            )
        if not have_color and have_artist:
            self._color_artist.hide()
            self._color_artist = None

        # Draw an outline if the user requested one.

        have_artist = self._outline_artist is not None
        have_outline = self._outline is not None

        if have_outline and have_artist:
            self._outline_artist.rect = apparent_rect
            self._outline_artist.color = self._outline

        if have_outline and not have_artist:
            self._outline_artist = Outline(
                    rect=apparent_rect,
                    color=self._outline, 
                    batch=self._batch,
                    group=self._outline_group,
            )
        if not have_outline and have_artist:
            self._outline_artist.hide()
            self._outline_artist = None

        # Decide which images to tile.

        vtile_flags = defaultdict(lambda: False)
        htile_flags = defaultdict(lambda: False)

        for ij in (1,0), (1,1), (1,2):
            vtile_flags[ij] = self._vtile
        for ij in (0,1), (1,1), (2,1):
            htile_flags[ij] = self._htile

        # Draw all the images that the user provided.  The logic is a little 
        # complicated to deal with the fact the we might have to add or remove 
        # tile artists.

        image_keys = set(self._tile_images)
        artist_keys = set(self._tile_artists)

        artists_to_add = image_keys - artist_keys
        artists_to_update = image_keys & artist_keys
        artists_to_remove = artist_keys - image_keys

        for ij in artists_to_add:
            self._tile_artists[ij] = Tile(
                    rect=tile_rects[ij],
                    image=self._tile_images[ij],
                    vtile=vtile_flags[ij],
                    htile=htile_flags[ij],
                    batch=self._batch,
                    group=self._tile_group,
            )
        for ij in artists_to_update:
            self._tile_artists[ij].rect = tile_rects[ij]
            self._tile_artists[ij].set_image(
                    self._tile_images[ij],
                    vtile=vtile_flags[ij],
                    htile=htile_flags[ij],
            )
        for ij in artists_to_remove:
            self._tile_artists[ij].hide()
            del self._tile_artists[ij]

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        if self._rect != new_rect:
            self._rect = new_rect
            self.update_rect()

    def update_rect(self):
        """
        Call this method to update the tile after you've made an in-place 
        change to its rectangle.
        """
        self._update_tiles()

    def get_min_size(self):
        self._grid.make_claim()
        return self._grid.min_width, self._grid.min_height

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        self._update_tiles()

    def get_outline(self):
        return self._outline

    def set_outline(self, new_outline):
        self._outline = new_outline
        self._update_tiles()

    def set_image(self, image):
        self.set_appearance(image=image)

    def get_appearance(self):
        images = self._tile_images.copy()
        images['color'] = self._color
        images['outline'] = self._outline
        images['htile'] = self._htile
        images['vtile'] = self._vtile
        return images

    def set_appearance(self, *, color=None, outline=None, image=None, 
            center=None, top=None, bottom=None, left=None, right=None, 
            top_left=None, top_right=None, bottom_left=None, bottom_right=None, 
            vtile='auto', htile='auto'):

        if image and center:
            raise UsageError("""\
specifying both 'image' and 'center' is ambiguous.

Both of these options specify an image that should go in the middle of the 
frame.  The only difference is that, if 'htile' or 'vtile' are set to 'auto' 
(the default value), 'center' enables tiling and 'image' doesn't.""")

        # Decide whether the background should tile in either dimension.

        auto_vtile = False
        auto_htile = False

        if top or bottom:
            auto_vtile = True
        if left or right:
            auto_htile = True
        if center and not (top or left or bottom or right):
            auto_vtile = True
            auto_htile = True

        self._vtile = auto_vtile if vtile == 'auto' else vtile
        self._htile = auto_htile if htile == 'auto' else htile

        # Store the images in a grid-like data structure.

        self._color = color
        self._outline = outline
        self._tile_images = {
                ij: img for ij, img in {
                    (0,0): top_left,
                    (0,1): top,
                    (0,2): top_right,
                    (1,0): left,
                    (1,1): center or image,
                    (1,2): right,
                    (2,0): bottom_left,
                    (2,1): bottom,
                    (2,2): bottom_right,
                }.items()
                if img is not None}

        self._grid.min_cell_rects = {
            ij: Rect.from_size(img.width, img.height)
            for ij, img in self._tile_images.items()}

        self._update_tiles()

    def get_batch(self):
        return self._batch

    def set_batch(self, new_batch):
        if self._batch is not new_batch:
            self._batch = new_batch
            if self._color_artist:
                self._color_artist.batch = new_batch
            for artist in self._tile_artists.values():
                artist.batch = new_batch

    def get_group(self):
        return self._group

    def set_group(self, new_group):
        if self._group != new_group:
            self._group = new_group
            self._update_group()

    def get_usage(self):
        return self._usage

    def set_usage(self, new_usage):
        if self._usage != new_usage:
            self._usage = new_usage
            self._color_artist = None
            self._tile_artists = {}
            self._update_tiles()

    @property
    def is_hidden(self):
        return self._hidden

    @property
    def is_empty(self):
        return not self._color and not self._tile_images

    def get_htile(self):
        return self._htile

    def get_vtile(self):
        return self._vtile

    def hide(self):
        if self._color_artist:
            self._color_artist.hide()
        if self._outline_artist:
            self._outline_artist.hide()
        for artist in self._tile_artists.values():
            artist.hide()

        self._color_artist = None
        self._outline_artist = None
        self._tile_artists = {}
        self._hidden = True

    def show(self):
        if self._hidden:
            self._hidden = False
            self._update_tiles()



