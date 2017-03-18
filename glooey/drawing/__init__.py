import math
import pyglet
import more_itertools
import autoprop
import vecrec
from vecrec import Vector, Rect
from collections import defaultdict
from pyglet.gl import *
from pyglet.graphics import Group, OrderedGroup
from glooey.helpers import *

# Color utilities

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
        if str in colors:
            return colors[str]
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

## Colors
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

colors = { #
        'red': red,
        'brown': brown,
        'orange': orange,
        'yellow': yellow,
        'green': green,
        'blue': blue,
        'purple': purple,
        'black': black,
        'dark': dark,
        'gray': gray,
        'light': light,
        'white': white }

rainbow_cycle = red, orange, yellow, green, blue, purple, brown


# Text utilities

def lorem_ipsum(num_sentences=None, num_paragraphs=None):

    paragraphs = [
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam justo sem, malesuada ut ultricies ac, bibendum eu neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean at tellus ut velit dignissim tincidunt. Curabitur euismod laoreet orci semper dignissim. Suspendisse potenti. Vivamus sed enim quis dui pulvinar pharetra. Duis condimentum ultricies ipsum, sed ornare leo vestibulum vitae. Sed ut justo massa, varius molestie diam. Sed lacus quam, tempor in dictum sed, posuere et diam. Maecenas tincidunt enim elementum turpis blandit tempus. Nam lectus justo, adipiscing vitae ultricies egestas, porta nec diam. Aenean ac neque tortor. Cras tempus lacus nec leo ultrices suscipit. Etiam sed aliquam tortor. Duis lacus metus, euismod ut viverra sit amet, pulvinar sed urna.',
        'Aenean ut metus in arcu mattis iaculis quis eu nisl. Donec ornare, massa ut vestibulum vestibulum, metus sapien pretium ante, eu vulputate lorem augue vestibulum orci. Donec consequat aliquam sagittis. Sed in tellus pretium tortor hendrerit cursus congue sit amet turpis. Sed neque lacus, lacinia ut consectetur eget, faucibus vitae lacus. Integer eu purus ac purus tempus mollis non sed dui. Vestibulum volutpat erat magna. Etiam nisl eros, eleifend a viverra sed, interdum sollicitudin erat. Integer a orci in dolor suscipit cursus. Maecenas hendrerit neque odio. Nulla orci orci, varius id viverra in, molestie vel lacus. Donec at odio quis augue bibendum lobortis nec ac urna. Ut lacinia hendrerit tortor mattis rhoncus. Proin nunc tortor, congue ac adipiscing sit amet, aliquet in lorem. Nulla blandit tempor arcu, ut tempus quam posuere eu. In magna neque, venenatis nec tincidunt vitae, lobortis eget nulla.',
        'Praesent sit amet nibh turpis, vitae lacinia metus. Ut nisi lacus, feugiat quis feugiat nec, pretium a diam. Aenean bibendum sem eget lorem ullamcorper mattis. Donec elementum purus vel felis vulputate pretium. Duis in ipsum est. Nulla consequat tempor sodales. Donec scelerisque enim eu tellus eleifend imperdiet. Quisque ullamcorper bibendum justo sit amet tincidunt. Donec tempus lacus quis diam varius placerat. Cras metus magna, congue sit amet pulvinar viverra, laoreet vel felis. Praesent sit amet consequat enim. Phasellus arcu nisl, volutpat et molestie a, sagittis a est. Maecenas tincidunt, sem non pharetra mollis, diam nisl ornare tellus, at euismod libero arcu ornare risus. Vestibulum laoreet sollicitudin purus in pharetra. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.',
        'Nullam pellentesque tempor bibendum. Praesent dictum turpis nec quam consectetur aliquam. Aliquam id turpis nunc. Pellentesque fermentum lacus at tortor auctor venenatis. Maecenas blandit dui lectus. Nunc pellentesque pharetra suscipit. Nullam et metus diam, a congue leo. Curabitur convallis augue in lectus scelerisque non rhoncus lorem molestie. Curabitur in mi a erat dictum pharetra iaculis eu diam.',
        'Nunc lorem magna, rhoncus sodales mattis quis, tincidunt eu mi. In ultrices, lectus ac porttitor tempor, odio nibh facilisis tortor, ac aliquet nisi ante non felis. Praesent ligula nisl, hendrerit ac volutpat non, varius quis tellus. Sed ornare faucibus elit eget faucibus. Nullam sem tellus, commodo id ullamcorper ut, imperdiet ac eros. Sed quis lorem id urna cursus laoreet et eget lacus. Nullam tristique semper sem, eget tempus sem pellentesque sit amet. Donec sed orci augue, convallis tempor tellus. Sed consequat commodo ante a pretium. Nulla et est mauris. Nullam at massa justo. Proin tempor arcu ac eros suscipit varius. Fusce vestibulum quam placerat tellus imperdiet et venenatis diam tristique. Sed pretium tempor tellus, consequat pulvinar massa pellentesque a.',
        'Nulla et lorem vel urna fringilla malesuada ut sit amet tortor. Donec id leo mi. Proin sagittis blandit lacus, placerat imperdiet justo pellentesque ac. Cras iaculis aliquam faucibus. Aenean urna nisi, laoreet ac fringilla dignissim, lacinia eget orci. Vivamus porta lacinia dapibus. Aenean molestie, augue sit amet blandit suscipit, tellus turpis ullamcorper purus, ut pretium turpis lorem quis neque. Pellentesque porta dui at arcu mollis tristique. Suspendisse feugiat felis quis felis sollicitudin porttitor.',
        'Morbi vestibulum, massa quis posuere facilisis, quam lacus porttitor tortor, id fringilla elit velit ac felis. Fusce at luctus risus. Mauris bibendum diam quis odio auctor quis porta massa pellentesque. Proin congue, nisl eu feugiat faucibus, justo orci congue neque, a porta tellus ipsum accumsan turpis. Ut neque enim, dignissim nec fermentum sed, laoreet id orci. Duis fringilla, elit vel tempus porttitor, purus tellus dapibus nisl, eu scelerisque diam lorem vel ante. Ut tempor, urna nec bibendum facilisis, sapien dui ornare lectus, at tempor ligula diam sit amet ligula. Sed a dui in ipsum eleifend egestas.',
        'Quisque ornare fringilla velit, et tincidunt purus convallis vel. Sed venenatis, risus vitae volutpat rhoncus, sapien lorem lacinia elit, id dictum sapien dui vitae lorem. Praesent aliquet accumsan eros quis tempor. Suspendisse eget justo quis arcu bibendum adipiscing. Phasellus quis erat nec massa elementum porta. Nam venenatis elementum mi vel porta. Nunc vel augue non tellus euismod convallis. Curabitur commodo augue vel augue ultrices in fringilla nunc cursus. Mauris auctor laoreet neque, id gravida velit suscipit eget. Maecenas eget libero in lacus auctor feugiat. Pellentesque in lectus felis, eu dictum tortor. Aenean sagittis, massa malesuada dapibus tincidunt, leo massa imperdiet ante, nec mollis nisl turpis in orci. Proin ut purus et eros sagittis volutpat.',
        'Donec molestie sem et metus bibendum convallis semper arcu imperdiet. Curabitur quam libero, fermentum vel adipiscing a, cursus at neque. Maecenas cursus risus vestibulum diam ultricies rutrum. Nullam in enim vel lorem accumsan pulvinar. Cras eget viverra turpis. Sed eget lectus urna, eget venenatis libero. Donec porta libero eu est pulvinar pretium. Ut lectus arcu, aliquam et vestibulum euismod, mattis at orci. Fusce dolor lorem, bibendum a dignissim ut, facilisis eu enim. Morbi erat nibh, interdum non ultricies non, porta ac lacus. Curabitur et nunc nec turpis convallis ullamcorper eget vitae mi.',
        'Curabitur porta molestie sapien, non rhoncus turpis gravida vel. Ut est lacus, elementum eu pretium sit amet, tristique vel orci. Praesent quis suscipit urna. Donec pellentesque molestie tellus sit amet fringilla. Etiam tempus viverra ipsum et tempus. Nunc ut odio imperdiet lorem malesuada bibendum. In aliquam ligula eu sem ullamcorper pulvinar. Quisque sollicitudin placerat dolor et porttitor. Nulla adipiscing lorem id libero aliquet interdum. Suspendisse vehicula fermentum congue. Cras fringilla nisl vitae lectus mollis viverra. Aliquam pharetra lobortis risus, a elementum elit condimentum in. Aenean tincidunt varius faucibus. Nulla non nisi lorem. Suspendisse id sapien a enim lobortis aliquam.',
        'Aliquam erat volutpat. Maecenas neque leo, mattis eu pretium vel, mattis in ante. Nullam sagittis leo diam. Quisque tempor magna in justo vestibulum eget egestas nibh pellentesque. Pellentesque in enim vitae velit pellentesque hendrerit. Cras ultricies, dui et imperdiet gravida, nunc nisl cursus tortor, sit amet porttitor dolor nibh a justo. Praesent ut mauris vitae turpis lobortis scelerisque a nec ligula. Donec turpis erat, iaculis vel dapibus vel, varius id lorem. Integer et enim erat, at eleifend libero.',
        'Phasellus id mi ut nunc cursus pellentesque. Aliquam erat volutpat. Vivamus pretium posuere tellus, ac aliquet metus iaculis eget. Curabitur in mi enim. Duis pretium pretium dui, ut iaculis ipsum scelerisque ut. Proin quam dolor, eleifend et porta vitae, cursus molestie lectus. Aenean dignissim laoreet consectetur. Cras iaculis, lectus imperdiet condimentum suscipit, metus nisi egestas arcu, in tempus sem ipsum eu eros. Vestibulum a orci in elit congue euismod quis quis nisi.',
        'In quis urna leo, at malesuada ipsum. Vestibulum sollicitudin ullamcorper hendrerit. Vestibulum vestibulum mi sodales nulla sagittis commodo. Maecenas nisi lorem, placerat vel aliquet quis, dictum ac ligula. Vestibulum egestas accumsan accumsan. Aenean lobortis pharetra erat convallis pretium. Aliquam consequat facilisis porta. Cras hendrerit nunc et mauris egestas hendrerit. Proin rhoncus, mi id ullamcorper pharetra, ipsum sapien blandit turpis, et ultricies purus neque eget justo. Quisque sodales, nisi in cursus rutrum, elit nibh volutpat lacus, nec sollicitudin erat leo at lectus. Morbi ac dolor mi, vel ultricies quam.',
        'Sed hendrerit nisl id lectus cursus in adipiscing lorem rutrum. Morbi nisl justo, egestas ac aliquet at, scelerisque luctus sapien. Donec sollicitudin elementum mattis. Praesent semper, ante euismod accumsan gravida, ante neque convallis augue, quis vulputate erat nunc vitae tellus. Duis ac lectus ullamcorper purus commodo luctus. Etiam quis augue in purus molestie imperdiet. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam posuere commodo turpis, at pulvinar tortor scelerisque et. Nam vulputate dui sed magna interdum sollicitudin. Nam pulvinar euismod enim vitae malesuada. Aenean non molestie leo. Pellentesque quis lacus mi, et ornare nibh. Etiam pharetra, odio vitae euismod faucibus, nunc urna pulvinar felis, eget molestie est enim sit amet sapien. Vivamus eu neque nulla.',
        'Mauris eget nibh ut augue malesuada tristique nec quis urna. Vestibulum faucibus, mauris sed posuere volutpat, felis lacus vulputate felis, eget luctus lorem nulla sed velit. Proin et purus nec quam tristique cursus. Nullam adipiscing tortor imperdiet purus facilisis eu luctus nulla vestibulum. Sed pulvinar risus sollicitudin risus fringilla et hendrerit lorem accumsan. Vestibulum venenatis est sit amet nunc gravida nec aliquam arcu adipiscing. Nam quis aliquet mauris. Cras nec neque vitae tellus posuere posuere.',
        'Nulla facilisi. Vestibulum sit amet dui turpis. Aliquam erat volutpat. In hac habitasse platea dictumst. Morbi in enim nec massa semper tincidunt. Ut fermentum iaculis dui, sed adipiscing dolor porta at. Nam hendrerit libero non nisi ornare eu cursus mauris accumsan. Ut ullamcorper, odio vel ultrices suscipit, metus libero ornare dui, non dapibus est dui vehicula ipsum.',
        'Nam diam sapien, lacinia vel sollicitudin interdum, faucibus aliquam enim. Mauris tristique iaculis purus eu lacinia. Suspendisse condimentum, dolor a euismod lacinia, leo orci pellentesque orci, non rhoncus turpis lorem sed lacus. Integer velit nisl, rutrum sit amet posuere at, vulputate ultrices tortor. Nullam pharetra, orci tempor dapibus elementum, felis nulla lacinia nunc, quis ultricies dui lectus dictum diam. Praesent eu velit magna, eu lacinia leo. Duis sit amet bibendum dui. Duis tincidunt vulputate dolor eu euismod. Pellentesque nisl sem, mollis ac venenatis a, facilisis vitae ligula. Vivamus sem leo, vestibulum tincidunt iaculis nec, tristique tincidunt mi. Suspendisse imperdiet elit vitae turpis ullamcorper luctus. Aenean in augue mauris. Vivamus nisi libero, dignissim non consectetur sodales, fermentum at sem. Nulla tincidunt fringilla justo quis pulvinar. Nam ac sem sed diam pellentesque egestas vitae ac nisi. Praesent scelerisque dapibus mi vitae tempor.',
        'Donec tempor, massa non pulvinar suscipit, justo dolor pharetra nisl, ut semper libero lorem non tortor. Integer dapibus arcu viverra nisi hendrerit mattis et ut mauris. Maecenas pulvinar, orci vitae ultricies egestas, orci nisi rutrum justo, eu volutpat nibh odio ac purus. Nulla pellentesque sem eget arcu imperdiet ullamcorper. Curabitur nec magna massa. Morbi lobortis urna sed ligula commodo viverra. Pellentesque molestie, ipsum nec faucibus mollis, neque purus sodales sapien, in convallis nisi libero et lorem. Ut sed rutrum leo. Aliquam eleifend, felis quis ullamcorper consequat, dolor mi vulputate ipsum, lobortis ultricies felis nulla at augue.',
        'Ut gravida porttitor arcu, malesuada mollis urna vehicula nec. Suspendisse sagittis nulla condimentum libero lacinia sed dapibus dui egestas. Etiam convallis congue ipsum, eu fermentum turpis rutrum id. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Ut nunc eros, sagittis a venenatis et, interdum in leo. Curabitur urna magna, volutpat in mattis ut, adipiscing et ligula. Nam dignissim mattis accumsan. Nulla vehicula felis vel turpis tempus hendrerit. Phasellus rhoncus vulputate massa, tincidunt euismod dui porttitor ac. Sed ut sapien quam, ac egestas odio. Pellentesque at aliquet ante. Donec rhoncus ornare lacus eu ullamcorper. Vestibulum sit amet hendrerit magna. Nulla sed diam nulla.',
        'Nulla vestibulum sagittis arcu in egestas. Aliquam sed ante justo. Quisque nec dolor nibh, sed feugiat mi. Etiam lorem elit, interdum eu tempor nec, tincidunt eu risus. Fusce id libero augue. Curabitur ultrices, lorem eget mollis fringilla, dolor leo euismod tellus, congue luctus nisi purus vitae urna. Suspendisse tempor orci accumsan sem pretium at accumsan augue tristique. Proin sed turpis at mi feugiat lacinia a nec sem. Suspendisse vel facilisis leo. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Duis ornare enim nec ante adipiscing tincidunt. Maecenas ut justo iaculis leo vestibulum blandit quis vitae mauris. Proin in vestibulum massa. ',
    ]

    if num_paragraphs:
        paragraphs = paragraphs[:num_paragraphs]

    text = '\n\n'.join(paragraphs)
    sentences = text.split('.')

    if num_sentences:
        sentences = sentences[:num_paragraphs]

    return '.'.join(sentences)


# Drawing utilities

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

        if not hidden:
            self._create_vertex_list()
            self._update_vertex_list()

    def get_batch(self):
        return self._batch

    def set_batch(self, new_batch):
        if self._batch is not new_batch:
            self._batch.migrate(
                    self._vertex_list, self._mode, self._group, new_batch)

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
        self._vertex_list.delete()
        self._vertex_list = None

    def unhide(self):
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

    def __init__(self, rect=None, color=green, *,
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

    def __init__(self, rect, color=green, *,
            batch=None, group=None, usage='static', hidden=False):

        self._rect = rect
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
            self.vertex_list.vertices = (
                    self._rect.bottom_left.tuple +
                    self._rect.bottom_right.tuple +
                    self._rect.bottom_right.tuple +
                    self._rect.top_right.tuple +
                    self._rect.top_right.tuple +
                    self._rect.top_left.tuple +
                    self._rect.top_left.tuple +
                    self._rect.bottom_left.tuple
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

    def __init__(self, *, rect=None, color=None, image=None, center=None, 
            top=None, bottom=None, left=None, right=None, top_left=None, 
            top_right=None, bottom_left=None, bottom_right=None, vtile='auto', 
            htile='auto', batch=None, group=None, usage='static', hidden=False):

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
        self.set_images(
                color=color,
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
        self._tile_group = pyglet.graphics.OrderedGroup(1, self._group)
        if self._color_artist:
            self._color_artist.group = self._color_group
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

        # Draw a colored rectangle behind everything else if the user provided 
        # a color.

        have_artist = self._color_artist is not None
        have_color = self._color is not None
        color_rect = self._grid.rect if self._tile_images else self._rect

        if have_color and have_artist:
            self._color_artist.rect = color_rect
            self._color_artist.color = self._color

        if have_color and not have_artist:
            self._color_artist = Rectangle(
                    rect=color_rect,
                    color=self._color, 
                    batch=self._batch,
                    group=self._color_group,
            )
        if not have_color and have_artist:
            self._color_artist.hide()
            self._color_artist = None

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

    def get_images(self):
        images = self._tile_images.copy()
        images['color'] = self._color
        images['htile'] = self._htile
        images['vtile'] = self._vtile
        return images

    def set_images(self, *, color=None, image=None, center=None, top=None, 
            bottom=None, left=None, right=None, top_left=None, top_right=None, 
            bottom_left=None, bottom_right=None, vtile='auto', htile='auto'):

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

    def set_image(self, image):
        self.set_images(image=image)

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

    def hide(self):
        if self._color_artist:
            self._color_artist.hide()
        for artist in self._tile_artists.values():
            artist.hide()

        self._color_artist = None
        self._tile_artists = {}
        self._hidden = True

    def unhide(self):
        if self._hidden:
            self._hidden = False
            self._update_tiles()



# Clipping mask utilities

class StencilGroup(Group):

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


class StencilMask(OrderedGroup):

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


class WhereStencilIs(OrderedGroup):

    def __init__(self, parent=None, order=1):
        super().__init__(order, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00)
        pyglet.gl.glStencilFunc(GL_EQUAL, 1, 0xFF)

    def unset_state(self):
        pass


class WhereStencilIsnt(OrderedGroup):

    def __init__(self, parent=None, order=1):
        super().__init__(order, parent)

    def set_state(self):
        from pyglet.gl import GL_EQUAL

        pyglet.gl.glStencilMask(0x00);
        pyglet.gl.glStencilFunc(GL_EQUAL, 0, 0xFF)

    def unset_state(self):
        pass



class ScissorGroup(Group):

    def __init__(self, rect=None, parent=None):
        super().__init__(parent)
        self.rect = rect

    def set_state(self):
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_SCISSOR_TEST)
        glScissor(
                int(self.rect.left),
                int(self.rect.bottom),
                int(self.rect.width),
                int(self.rect.height),
        )

    def unset_state(self):
        glPopAttrib(GL_ENABLE_BIT)



# Alignment utilities

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
    try:
        alignment_func = alignments[key_or_function]
    except KeyError:
        alignment_func = key_or_function

    alignment_func(child_rect, parent_rect)

def fixed_size_align(key_or_function, child_rect, parent_rect):
    fixed_size = child_rect.size
    align(key_or_function, child_rect, parent_rect)
    if child_rect.size != fixed_size:
        raise UsageError(f"a fixed-sized alignment was required, but {repr(key_or_function)} resized the rect being aligned from {'x'.join(fixed_size)} to {'x'.join(child_rect.size)}.")


# Rectangle placement utilities

@autoprop
class Grid:

    def __init__(self, *, bounding_rect=None, min_cell_rects={},
            num_rows=0, num_cols=0, padding=None, inner_padding=None, 
            outer_padding=None, row_heights={}, col_widths={},
            default_row_height='expand', default_col_width='expand'):

        # Attributes that the user can set to affect the shape of the grid.  
        self._bounding_rect = bounding_rect or Rect.null()
        self._min_cell_rects = min_cell_rects
        self._requested_num_rows = num_rows
        self._requested_num_cols = num_cols
        self._inner_padding = first_not_none((inner_padding, padding, 0))
        self._outer_padding = first_not_none((outer_padding, padding, 0))
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
        self._padding_height = 0
        self._padding_width = 0
        self._min_height = 0
        self._min_width = 0
        self._row_heights = {}
        self._col_widths = {}
        self._width = 0
        self._height = 0
        self._row_tops = {}
        self._col_lefts = {}
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

    def find_cell_under_mouse(self, x, y):
        # The >=/<= comparisons in this method were chosen to be compatible 
        # with the comparisons in Widget.is_under_mouse().  That method counts 
        # points that are on any edge of a widget as being over that widget.  
        # The >=/<= comparisons do the same thing here.
        #
        # I initially wrote this method using an inclusive operator on one side 
        # and an exclusive one on the other, to avoid any ambiguity in the case 
        # where there's no padding.  For example, imagine a 2x2 grid with no 
        # padding.  In theory, the point exactly in the middle is over all four 
        # cells.  In practice, the algorithm will identify the top-left-most 
        # cell first and return it.  So the algorithm isn't really ambiguous, 
        # but it is more dependent on what's really an implementation detail.

        # Find the row the mouse is over.
        for i in range(self._num_rows):
            row_top = self._row_tops[i]
            row_bottom = row_top - self._row_heights[i]
            if row_top >= y >= row_bottom:
                break
        else:
            return None

        # Find the col the mouse is over.
        for j in range(self._num_cols):
            col_left = self._col_lefts[j]
            col_right = col_left + self._col_widths[j]
            if col_left <= x <= col_right:
                break
        else:
            return None

        return i, j

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_rect(self):
        return Rect.from_size(self._width, self._height)

    def get_min_width(self):
        return self._min_width

    def get_min_height(self):
        return self._min_height

    min_height = property(get_min_height)

    def get_min_bounding_rect(self):
        return Rect.from_size(self._min_width, self._min_height)

    def get_cell_rects(self):
        return self._cell_rects

    cell_rects = property(get_cell_rects)

    def get_bounding_rect(self):
        return self._bounding_rect

    def set_bounding_rect(self, new_rect):
        if self._bounding_rect != new_rect:
            self._bounding_rect = new_rect
            self._invalidate_cells()

    def get_min_cell_rect(self, i, j):
        return self._min_cell_rects[i,j]

    def set_min_cell_rect(self, i, j, new_rect):
        if (i,j) not in self._min_cell_rects or \
                self._min_cell_rects[i,j] != new_rect:
            self._min_cell_rects[i,j] = new_rect
            self._invalidate_shape()

    def del_min_cell_rect(self, i, j):
        if (i,j) in self._min_cell_rects:
            del self._min_cell_rects[i,j]
            self._invalidate_shape()

    def get_min_cell_rects(self):
        return self._min_cell_rects

    def set_min_cell_rects(self, new_rects):
        if self._min_cell_rects != new_rects:
            self._min_cell_rects = new_rects
            self._invalidate_shape()

    def del_min_cell_rects(self):
        if self._min_cell_rects:
            self._min_cell_rects = {}
            self._invalidate_shape()

    def get_num_rows(self):
        return self._num_rows

    def set_num_rows(self, new_num):
        self._requested_num_rows = new_num
        self._invalidate_shape()

    def get_num_cols(self):
        return self._num_cols

    def set_num_cols(self, new_num):
        self._requested_num_cols = new_num
        self._invalidate_shape()

    def get_padding(self):
        return self._inner_padding, self._outer_padding

    def set_padding(self, new_padding):
        self._inner_padding = new_padding
        self._outer_padding = new_padding
        self._invalidate_claim()

    def get_inner_padding(self):
        return self._inner_padding

    def set_inner_padding(self, new_padding):
        self._inner_padding = new_padding
        self._invalidate_claim()

    def get_outer_padding(self):
        return self._outer_padding

    def set_outer_padding(self, new_padding):
        self._outer_padding = new_padding
        self._invalidate_claim()

    def get_row_height(self, i):
        return self._row_heights[i]

    def set_row_height(self, i, new_height):
        self._requested_row_heights[i] = new_height
        self._invalidate_claim()

    def del_row_height(self, i):
        if i in self._requested_row_heights:
            del self._requested_row_heights[i]
            self._invalidate_claim()

    def get_row_heights(self):
        return self._row_heights

    def set_row_heights(self, new_heights):
        self._requested_row_heights = new_heights
        self._invalidate_claim()

    def del_row_heights(self):
        self._requested_row_heights = {}
        self._invalidate_claim()

    def get_col_width(self, j):
        return self._col_widths[j]

    def set_col_width(self, j, new_width):
        self._requested_col_widths[j] = new_width
        self._invalidate_claim()

    def del_col_width(self, j):
        if j in self._requested_col_widths:
            del self._requested_col_widths[j]
            self._invalidate_claim()

    def get_col_widths(self):
        return self._col_widths

    def set_col_widths(self, new_widths):
        self._requested_col_widths = new_widths
        self._invalidate_claim()

    def del_col_widths(self):
        self._requested_col_widths = {}
        self._invalidate_claim()

    def get_default_row_height(self):
        return self._default_row_height

    def set_default_row_height(self, new_height):
        self._default_row_height = new_height
        self._invalidate_claim()

    def get_default_col_width(self):
        return self._default_col_width

    def set_default_col_width(self, new_width):
        self._default_col_width = new_width
        self._invalidate_claim()

    def get_requested_num_rows(self):
        return self._requested_num_rows

    def get_requested_num_cols(self):
        return self._requested_num_cols

    requested_num_cols = property(get_requested_num_cols)

    def get_requested_row_height(self, i):
        return self._requested_row_heights[i]

    def get_requested_row_heights(self):
        return self._requested_row_heights

    def get_requested_col_width(self, i):
        return self._requested_col_widths[i]

    def get_requested_col_widths(self):
        return self._requested_col_widths

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
            self._find_padding_height()
            self._find_padding_width()
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

    def _find_padding_height(self):
        self._padding_height = \
                + self._inner_padding * (self._num_rows - 1) \
                + self._outer_padding * 2

    def _find_padding_width(self):
        self._padding_width = \
                + self._inner_padding * (self._num_cols - 1) \
                + self._outer_padding * 2

    def _find_min_height(self):
        min_expandable_height = max(
                self._min_expandable_row_heights.values() or [0])
        self._min_height = \
                + sum(self._fixed_row_heights.values()) \
                + min_expandable_height * self._num_expandable_rows \
                + self._padding_height

    def _find_min_width(self):
        min_expandable_width = max(
                self._min_expandable_col_widths.values() or [0])
        self._min_width = \
                + sum(self._fixed_col_widths.values()) \
                + min_expandable_width * self._num_expandable_cols \
                + self._padding_width

    def _find_row_heights(self):
        self._row_heights = self._fixed_row_heights.copy()

        if self._num_expandable_rows:
            expandable_row_height = (
                    + self._bounding_rect.height
                    - sum(self._fixed_row_heights.values())
                    - self._padding_height
                    ) / self._num_expandable_rows

            for i in self._expandable_rows:
                self._row_heights[i] = expandable_row_height

        self._height = \
                + sum(self._row_heights.values()) \
                + self._padding_height

    def _find_col_widths(self):
        self._col_widths = self._fixed_col_widths.copy()

        if self._num_expandable_cols:
            expandable_col_width = (
                    + self._bounding_rect.width
                    - sum(self._fixed_col_widths.values())
                    - self._padding_width
                    ) / self._num_expandable_cols

            for j in self._expandable_cols:
                self._col_widths[j] = expandable_col_width

        self._width = \
                + sum(self._col_widths.values()) \
                + self._padding_width

    def _find_cell_rects(self):
        self._row_tops = {}
        self._col_lefts = {}
        self._cell_rects = {}

        top_cursor = self._bounding_rect.top

        for i in range(self._num_rows):
            top_cursor -= self._get_row_padding(i)
            left_cursor = self._bounding_rect.left
            row_height = self._row_heights[i]
            self._row_tops[i] = top_cursor

            for j in range(self._num_cols):
                left_cursor += self._get_col_padding(j)
                col_width = self._col_widths[j]

                self._cell_rects[i,j] = Rect.from_size(col_width, row_height)
                self._cell_rects[i,j].top_left = left_cursor, top_cursor
                self._col_lefts[j] = left_cursor

                left_cursor += col_width
            top_cursor -= row_height

    def _get_requested_row_height(self, i):
        return self._requested_row_heights.get(i, self._default_row_height)

    def _get_requested_col_width(self, j):
        return self._requested_col_widths.get(j, self._default_col_width)

    def _get_row_padding(self, i):
        return self._outer_padding if i == 0 else self._inner_padding

    def _get_col_padding(self, j):
        return self._outer_padding if j == 0 else self._inner_padding



def make_grid(rect, cells={}, num_rows=0, num_cols=0, padding=None,
        inner_padding=None, outer_padding=None, row_heights={}, col_widths={}, 
        default_row_height='expand', default_col_width='expand'):
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
            inner_padding=inner_padding,
            outer_padding=outer_padding,
            row_heights=row_heights,
            col_widths=col_widths,
            default_row_height=default_row_height,
            default_col_width=default_col_width,
    )
    return grid.make_cells()
