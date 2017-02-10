import pyglet
import autoprop

from vecrec import Vector, Rect
from debugtools import pprint, debug
from . import drawing, containers
from .widget import Widget
from .containers import Deck

@autoprop
class Clickable(Widget):

    def __init__(self):
        super().__init__()
        self._last_rollover_event = 'base'
        self._mouse_state = 'base'
        self._active_state = True
        self._double_click_timer = 0

    def deactivate(self):
        self._active_state = False
        self._dispatch_rollover_event()

    def reactivate(self):
        self._active_state = True
        self._dispatch_rollover_event()

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        self._mouse_state = 'down'
        self._dispatch_rollover_event()

    def on_mouse_release(self, x, y, button, modifiers):
        import time
        super().on_mouse_release(x, y, button, modifiers)

        if self._active_state and self._mouse_state == 'down':
            self.dispatch_event('on_click', self)

            # Two clicks within 500 ms triggers a double-click.
            if time.perf_counter() - self._double_click_timer < 0.5:
                self.dispatch_event('on_double_click', self)
                self._double_click_timer = 0
            else:
                self._double_click_timer = time.perf_counter()

        self._mouse_state = 'over'
        self._dispatch_rollover_event()

    def on_mouse_enter(self, x, y):
        super().on_mouse_enter(x, y)
        self._mouse_state = 'over'
        self._dispatch_rollover_event()

    def on_mouse_leave(self, x, y):
        super().on_mouse_leave(x, y)
        self._mouse_state = 'base'
        self._dispatch_rollover_event()

    def on_mouse_drag_leave(self, x, y):
        super().on_mouse_drag_leave(x, y)
        self._mouse = 'base'
        self._dispatch_rollover_event()
    
    @property
    def is_active(self):
        return self._active_state

    def get_rollover(self):
        return self._last_rollover_event

    def _dispatch_rollover_event(self):
        rollover_event = self._mouse_state if self._active_state else 'off'
        if rollover_event != self._last_rollover_event:
            self.dispatch_event('on_rollover', rollover_event, self._last_rollover_event)
            self._last_rollover_event = rollover_event


Clickable.register_event_type('on_click')
Clickable.register_event_type('on_double_click')
Clickable.register_event_type('on_rollover')

@autoprop
class Rollover(Deck):

    def __init__(self, clickable, initial_state, **widgets):
        super().__init__(initial_state, **widgets)
        clickable.push_handlers(self.on_rollover)

    def on_rollover(self, new_state, old_state):
        if new_state not in self.known_states and new_state == 'down':
            new_state = 'over'

        if new_state not in self.known_states and new_state == 'over':
            new_state = 'base'

        self.set_state(new_state)


class PlaceHolder(Clickable):

    def __init__(self, width=0, height=0, color=drawing.green, align='fill'):
        super().__init__()
        self.color = color
        self.width = width
        self.height = height
        self.vertex_list = None
        self.alignment = align

    def do_claim(self):
        return self.width, self.height

    def do_regroup(self):
        if self.vertex_list is not None:
            self.batch.migrate(
                    self.vertex_list, pyglet.gl.GL_LINES,
                    self.group, self.batch)

    def do_draw(self):
        if self.vertex_list is None:
            self.vertex_list = self.batch.add(
                    12, pyglet.gl.GL_LINES, self.group, 'v2f', 'c4B')

        top_left = self.rect.top_left
        top_right = self.rect.top_right
        bottom_left = self.rect.bottom_left
        bottom_right = self.rect.bottom_right

        # Originally I used GL_LINE_STRIP, but I couldn't figure out how to 
        # stop the place holders from connecting to each other (i.e. I couldn't 
        # figure out how to break the line strip).  Now I'm just using GL_LINES 
        # instead.

        self.vertex_list.vertices = (
                # the outline
                bottom_left.tuple + bottom_right.tuple + 
                bottom_right.tuple + top_right.tuple + 
                top_right.tuple + top_left.tuple + 
                top_left.tuple + bottom_left.tuple + 

                # the cross
                bottom_left.tuple + top_right.tuple + 
                bottom_right.tuple + top_left.tuple
        ) 
        self.vertex_list.colors = 12 * self.color.tuple

    def do_undraw(self):
        if self.vertex_list is not None:
            self.vertex_list.delete()
            self.vertex_list = None


class EventLogger(PlaceHolder):

    def on_click(self, widget):
        print(f'on_click(widget={widget})')

    def on_double_click(self, widget):
        print(f'on_double_click(widget={widget})')

    def on_rollover(self, new_state, old_state):
        print(f'on_rollover({new_state} {old_state})')

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        print(f'on_mouse_press(x={x}, y={y}, button={button}, modifiers={modifiers})')

    def on_mouse_release(self, x, y, button, modifiers):
        super().on_mouse_release(x, y, button, modifiers)
        print(f'on_mouse_release(x={x}, y={y}, button={button}, modifiers={modifiers})')

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        print(f'on_mouse_motion(x={x}, y={y}, dx={dx}, dy={dy})')

    def on_mouse_enter(self, x, y):
        super().on_mouse_enter(x, y)
        print(f'on_mouse_enter(x={x}, y={y})')

    def on_mouse_leave(self, x, y):
        super().on_mouse_leave(x, y)
        print(f'on_mouse_leave(x={x}, y={y})')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        print(f'on_mouse_drag(x={x}, y={y}, dx={dx}, dy={dy}, buttons={buttons}, modifiers={modifiers})')

    def on_mouse_drag_enter(self, x, y):
        super().on_mouse_drag_enter(x, y)
        print(f'on_mouse_drag_enter(x={x}, y={y})')

    def on_mouse_drag_leave(self, x, y):
        super().on_mouse_drag_leave(x, y)
        print(f'on_mouse_drag_leave(x={x}, y={y})')

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)
        print(f'on_mouse_scroll(x={x}, y={y}, scroll_x={scroll_x}, scroll_y={scroll_y})')



@autoprop
class Label(Widget):
    default_text = ""
    default_font_name = None
    default_font_size = None
    default_bold = None
    default_italic = None
    default_underline = None
    default_kerning = None
    default_baseline = None
    default_color = 'green'
    default_background_color = None
    default_text_alignment = None
    default_line_spacing = None

    def __init__(self, text="", **style):
        super().__init__()
        self._layout = None
        self._text = text or self.default_text
        self._line_wrap_width = 0
        self._style = {}
        self.set_style(
                font_name=self.default_font_name,
                font_size=self.default_font_size,
                bold=self.default_bold,
                italic=self.default_italic,
                underline=self.default_underline,
                kerning=self.default_kerning,
                baseline=self.default_baseline,
                color=self.default_color,
                background_color=self.default_background_color,
                align=self.default_text_alignment,
                line_spacing=self.default_line_spacing,
        )
        self.set_style(**style)

    def do_claim(self):
        # Make sure the label's text and style are up-to-date before we request 
        # space.  Be careful!  This means that do_draw() can be called before 
        # the widget has self.rect or self.group, which usually cannot happen.
        self.do_draw(ignore_rect=True)

        # Return the amount of space needed to render the label.
        return self._layout.content_width, self._layout.content_height

    def do_draw(self, ignore_rect=False):
        # Any time we need to draw this widget, just delete the underlying 
        # label object and make a new one.  This isn't any slower than keeping 
        # the old object, because all the vertex lists would be redrawn either 
        # way.  And this is more flexible, because it allows us to reset the 
        # batch, the group, and the wrap_lines attribute.
        if self._layout is not None:
            self._layout.delete()

        kwargs = {
                'multiline': True,
                'wrap_lines': False,
                'batch': self.batch,
                'group': self.group
        }
        # Enable line wrapping, if the user requested it.  The width of the 
        # label is set to the value given by the user when line-wrapping was 
        # enabled.  This will be overwritten a few lines later if the widget 
        # has been given a rectangle.
        if self._line_wrap_width:
            kwargs['width'] = self._line_wrap_width
            kwargs['wrap_lines'] = True
        
        # Usually self.rect is guaranteed to be set by the time this method is 
        # called, but that is not the case for this widget.  The do_claim() 
        # method needs to call do_draw() to see how much space the text will 
        # need, and that happens before self.rect is set (since it's part of 
        # the process of setting self.rect). 
        if not ignore_rect:
            kwargs['width'] = self.rect.width
            kwargs['height'] = self.rect.height

        # It's best to make a fresh document each time.  Previously I was 
        # storing the document as a member variable, but I ran into corner 
        # cases where the document would have an old style that wouldn't be 
        # compatible with the new TextLayout (specifically 'align' != 'left' if 
        # line wrapping is no loner enabled).
        document = pyglet.text.decode_text(self._text)
        self._layout = pyglet.text.layout.TextLayout(document, **kwargs)

        # Use begin_update() and end_update() to prevent the layout from 
        # generating new vertex lists until the styles and coordinates have 
        # been set.
        self._layout.begin_update()

        # The layout will crash if it doesn't have an explicit width and the 
        # style specifies an alignment.  I
        if self._layout.width is None:
            self._layout.width = self._layout.content_width

        document.set_style(0, len(self._text), self._style)

        if not ignore_rect:
            self._layout.x = self.rect.bottom_left.x
            self._layout.y = self.rect.bottom_left.y

        self._layout.end_update()

    def do_undraw(self):
        if self._layout is not None:
            self._layout.delete()

    def get_text(self):
        return self._text

    def set_text(self, text, width=None, **style):
        self._text = text
        if width is not None:
            self._line_wrap_width = width
        # This will repack.
        self.set_style(**style)

    def del_text(self):
        self.set_text("")

    def get_font_name(self):
        return self.get_style('font_name')

    def set_font_name(self, name):
        self.set_style(font_name=name)

    def del_font_name(self):
        return self.del_style('font_name')

    def get_font_size(self):
        return self.get_style('font_size')

    def set_font_size(self, size):
        self.set_style(font_size=size)

    def del_font_size(self):
        return self.del_style('font_size')

    def get_bold(self):
        return self.get_style('bold')

    def set_bold(self, bold):
        self.set_style(bold=bold)

    def del_bold(self):
        return self.del_style('bold')

    def get_italic(self):
        return self.get_style('italic')

    def set_italic(self, italic):
        self.set_style(italic=italic)

    def del_italic(self):
        return self.del_style('italic')

    def get_underline(self):
        return self.get_style('underline') is not None

    def set_underline(self, underline):
        self.set_style(underline=underline)

    def del_underline(self):
        return self.del_style('underline') is not None

    def get_kerning(self):
        return self.get_style('kerning')

    def set_kerning(self, kerning):
        self.set_style(kerning=kerning)

    def del_kerning(self):
        return self.del_style('kerning')

    def get_baseline(self):
        return self.get_style('baseline')

    def set_baseline(self, baseline):
        self.set_style(baseline=baseline)

    def del_baseline(self):
        return self.del_style('baseline')

    def get_color(self):
        return self.get_style('color')

    def set_color(self, color):
        self.set_style(color=color)

    def del_color(self):
        return self.del_style('color')

    def get_background_color(self):
        return self.get_style('background_color')

    def set_background_color(self, color):
        self.set_style(background_color=color)

    def del_background_color(self):
        return self.del_style('background_color')

    def get_text_alignment(self):
        return self.get_style('align')

    def set_text_alignment(self, alignment):
        self.set_style(align=alignment)

    def del_text_alignment(self):
        return self.del_style('align')

    def get_line_spacing(self):
        return self.get_style('line_spacing')

    def set_line_spacing(self, spacing):
        self.set_style(line_spacing=spacing)

    def del_line_spacing(self):
        self.del_style('line_spacing')

    def enable_line_wrap(self, width):
        self._line_wrap_width = width
        self.repack()

    def disable_line_wrap(self):
        self.enable_line_wrap(0)

    def get_style(self, style):
        return self._style.get(style)

    def set_style(self, **style):
        self._style.update({k:v for k,v in style.items() if v is not None})
        self._update_style()

    def del_style(self, style):
        del self._style[style]
        self._update_style()

    def _update_style(self):
        # I want users to be able to specify colors using strings or Color 
        # objects, but pyglet expects tuples, so make the conversion here.

        if 'color' in self._style:
            self._style['color'] = drawing.Color.from_anything(
                    self._style['color']).tuple

        if 'background_color' in self._style:
            self._style['background_color'] = drawing.Color.from_anything(
                    self._style['background_color']).tuple

        # I want the underline attribute to behave as a boolean, but in the 
        # TextLayout API it's a color.  So when it's set to either True or 
        # False, I need to translate that to either being a color or not being 
        # in the style dictionary.

        if 'underline' in self._style:
            if not self._style['underline']:
                del self._style['underline']
            else:
                self._style['underline'] = self.color

        self.repack()


@autoprop
class Image(Widget):
    default_image = None
    default_alignment = 'center'

    def __init__(self, image=None):
        super().__init__()
        self._image = image or self.default_image
        self._sprite = None

    def do_claim(self):
        if self.image is not None:
            return self.image.width, self.image.height
        else:
            return 0, 0

    def do_regroup(self):
        if self._sprite is not None:
            self._sprite.group = self.group

    def do_draw(self):
        if self.image is None:
            self.do_undraw()
            return

        if self._sprite is None:
            self._sprite = pyglet.sprite.Sprite(
                    self.image, batch=self.batch, group=self.group)
        else:
            self._sprite.image = self.image

        self._sprite.x = self.rect.left
        self._sprite.y = self.rect.bottom

    def do_undraw(self):
        if self._sprite is not None:
            self._sprite.delete()
            self._sprite = None

    def get_image(self):
        return self._image

    def set_image(self, new_image):
        if self._image is not new_image:
            self._image = new_image
            self.repack()

    def unset_image(self):
        self.set_image(None)


@autoprop
class Background(Widget):
    default_color = None
    default_center = None
    default_top = None
    default_bottom = None
    default_left = None
    default_right = None
    default_top_left = None
    default_top_right = None
    default_bottom_left = None
    default_bottom_right = None
    default_vtile = False
    default_htile = False

    def __init__(self, *, color=None, center=None, top=None, bottom=None, 
            left=None, right=None, top_left=None, top_right=None, 
            bottom_left=None, bottom_right=None, vtile=False, htile=False):

        super().__init__()
        self._artist = drawing.Background(
                color=color or self.default_color,
                center=center or self.default_center,
                top=top or self.default_top,
                bottom=bottom or self.default_bottom,
                left=left or self.default_left,
                right=right or self.default_right,
                top_left=top_left or self.default_top_left,
                top_right=top_right or self.default_top_right,
                bottom_left=bottom_left or self.default_bottom_left,
                bottom_right=bottom_right or self.default_bottom_right,
                vtile=vtile or self.default_vtile,
                htile=htile or self.default_htile,
                hidden=True,
        )

    def do_attach(self):
        self._artist.batch = self.batch

    def do_claim(self):
        return self._artist.min_size

    def do_resize(self):
        self._artist.rect = self.rect

    def do_regroup(self):
        self._artist.group = self.group

    def do_draw(self):
        self._artist.unhide()

    def do_undraw(self):
        self._artist.hide()

    def get_images(self):
        return self._artist.images

    def set_images(self, *, color=None, center=None, top=None, bottom=None, 
            left=None, right=None, top_left=None, top_right=None, 
            bottom_left=None, bottom_right=None, vtile=None, htile=None):

        self._artist.set_images(
                color=color,
                center=center,
                top=top,
                bottom=bottom,
                left=left,
                right=right,
                top_left=top_left,
                top_right=top_right,
                bottom_left=bottom_left,
                bottom_right=bottom_right,
                vtile=vtile,
                htile=htile,
        )
        self.repack()

    def set_image(self, image):
        self._artist.set_image(image)
        self.repack()

    @property
    def is_empty(self):
        return self._artist.is_empty


@autoprop
class Button(Clickable):
    Label = Label
    Image = Image
    Base = Background
    Over = Background
    Down = Background
    Off = Background

    default_label_layer = 3
    default_image_layer = 2
    default_background_layer = 1
    default_vtile = None
    default_htile = None
    default_alignment = 'center'

    def __init__(self, text='', image=None):
        super().__init__()
        self._stack = containers.Stack()
        self._label = self.Label()
        self._image = self.Image()
        self._background = Rollover(self, 'base')

        self.set_text(text)
        self.set_image(image)
        self.set_background(vtile=self.default_vtile, htile=self.default_htile)

        self._attach_child(self._stack)
        self._stack.insert(self._label, self.default_label_layer)
        self._stack.insert(self._image, self.default_image_layer)
        self._stack.insert(self._background, self.default_background_layer)

    def do_claim(self):
        return self._stack.claimed_size

    def get_text(self):
        return self._label.text

    def set_text(self, text, **style):
        self._label.set_text(text, **style)

    def del_text(self):
        del self._label.text

    def get_label(self):
        return self._label

    def set_label(self, label, placement=None):
        self._stack.remove(self._label)
        self._label = label
        self._stack.insert(
                self._label,
                self.default_label_layer,
                placement or self.default_label_placement,
        )

    def get_image(self):
        return self._image.image

    def set_image(self, image):
        self._image.set_image(image)

    def del_image(self):
        del self._image.image

    def set_background(self, *, 
            base=None,              over=None,              down=None,              off=None,
            base_color=None,        over_color=None,        down_color=None,        off_color=None,
            base_center=None,       over_center=None,       down_center=None,       off_center=None,
            base_top=None,          over_top=None,          down_top=None,          off_top=None, 
            base_bottom=None,       over_bottom=None,       down_bottom=None,       off_bottom=None, 
            base_left=None,         over_left=None,         down_left=None,         off_left=None,
            base_right=None,        over_right=None,        down_right=None,        off_right=None,
            base_top_left=None,     over_top_left=None,     down_top_left=None,     off_top_left=None,
            base_top_right=None,    over_top_right=None,    down_top_right=None,    off_top_right=None,
            base_bottom_left=None,  over_bottom_left=None,  down_bottom_left=None,  off_bottom_left=None,
            base_bottom_right=None, over_bottom_right=None, down_bottom_right=None, off_bottom_right=None,
            vtile=None, htile=None, placement=None):

        base_center = base_center or base
        over_center = over_center or over
        down_center = down_center or down
        off_center  = off_center  or off

        self._background.reset_states_if(
                lambda w: not w.is_empty,
                base=self.Base(
                    color        = base_color,
                    center       = base_center,
                    top          = base_top,         
                    bottom       = base_bottom,      
                    left         = base_left,        
                    right        = base_right,       
                    top_left     = base_top_left,    
                    top_right    = base_top_right,   
                    bottom_left  = base_bottom_left, 
                    bottom_right = base_bottom_right,
                    vtile        = vtile,
                    htile        = htile,
                ),
                over=self.Over(
                    color        = over_color,
                    center       = over_center,
                    top          = over_top,         
                    bottom       = over_bottom,      
                    left         = over_left,        
                    right        = over_right,       
                    top_left     = over_top_left,    
                    top_right    = over_top_right,   
                    bottom_left  = over_bottom_left, 
                    bottom_right = over_bottom_right,
                    vtile        = vtile,
                    htile        = htile,
                ),
                down=self.Down(
                    color        = down_color,
                    center       = down_center,
                    top          = down_top,         
                    bottom       = down_bottom,      
                    left         = down_left,        
                    right        = down_right,       
                    top_left     = down_top_left,    
                    top_right    = down_top_right,   
                    bottom_left  = down_bottom_left, 
                    bottom_right = down_bottom_right,
                    vtile        = vtile,
                    htile        = htile,
                ),
                off=self.Off(
                    color        = off_color,
                    center       = off_center,
                    top          = off_top,         
                    bottom       = off_bottom,      
                    left         = off_left,        
                    right        = off_right,       
                    top_left     = off_top_left,    
                    top_right    = off_top_right,   
                    bottom_left  = off_bottom_left, 
                    bottom_right = off_bottom_right,
                    vtile        = vtile,
                    htile        = htile,
                ),
        )

    def del_background(self):
        self.set_background()


@autoprop
class Checkbox(Clickable):

    default_checked_base = None; default_unchecked_base = None
    default_checked_over = None; default_unchecked_over = None
    default_checked_down = None; default_unchecked_down = None
    default_checked_off  = None; default_unchecked_off  = None
    default_alignment = 'center'

    def __init__(self, is_checked=False):
        super().__init__()
        self._deck = Deck(is_checked)
        self._attach_child(self._deck)
        self.set_images(
                checked_base=self.default_checked_base,
                checked_over=self.default_checked_over,
                checked_down=self.default_checked_down,
                checked_off=self.default_checked_off,
                unchecked_base=self.default_unchecked_base,
                unchecked_over=self.default_unchecked_over,
                unchecked_down=self.default_unchecked_down,
                unchecked_off=self.default_unchecked_off,
        )

    def do_claim(self):
        return self._deck.claimed_size

    def on_click(self, widget):
        self.toggle()

    def toggle(self):
        self._deck.state = not self._deck.state
        self.dispatch_event('on_toggle', self)

    def check(self):
        if not self.is_checked:
            self.toggle()

    def uncheck(self):
        if self.is_checked:
            self.toggle()

    @property
    def is_checked(self):
        return self._deck.state

    def set_images(self, *,
            checked_base=None, unchecked_base=None,
            checked_over=None, unchecked_over=None,
            checked_down=None, unchecked_down=None,
            checked_off=None,  unchecked_off=None):

        checked = Rollover(self, 'base')
        checked.add_states_if(
                lambda w: w.image is not None,
                base=Image(checked_base),
                over=Image(checked_over),
                down=Image(checked_down),
                off=Image(checked_off),
        )
        unchecked = Rollover(self, 'base')
        unchecked.add_states_if(
                lambda w: w.image is not None,
                base=Image(unchecked_base),
                over=Image(unchecked_over),
                down=Image(unchecked_down),
                off=Image(unchecked_off),
        )
        with self._deck.hold_updates():
            self._deck.add_state(True, checked)
            self._deck.add_state(False, unchecked)

    def unset_images(self):
        self._deck.clear_states()


Checkbox.register_event_type('on_toggle')

@autoprop
class RadioButton(Checkbox):

    def __init__(self, peers=None, *, is_checked=False, **images):
        super().__init__(is_checked=is_checked, **images)
        self.peers = peers if peers is not None else []

    def on_toggle(self, widget):
        if self.is_checked:
            for peer in self.peers:
                if peer is not self:
                    peer.uncheck()

    def get_peers(self):
        return self._peers

    def set_peers(self, peers):
        if self not in peers:
            peers.append(self)
        self._peers = peers



# Work in progress...

@autoprop
class Tooltip(Widget):

    def __init__(self, widget, layer=10):
        self._widget = widget
        self._widget.push_handlers(self)
        self._layer = layer

    def get_widget(self):
        return self._widget

    def set_widget(self, new_widget):
        self._widget.pop_handlers()
        self._widget = widget
        self._widget.push_handlers(self)

    def get_parent(self):
        return self._widget

    def get_layer(self):
        return self._layer

    def set_layer(self, new_layer):
        self._layer = new_layer
        self._update_rect()
        self._update_group()

    def on_attach(self):
        self._update_group()

    def draw_background(self):
        pass

    def _update_rect(self):
        pass

    def _update_group(self):
        if self.is_attached_to_gui:
            group = pyglet.graphics.OrderedGroup(self.root.group, self._layer)
            self.regroup(group)
