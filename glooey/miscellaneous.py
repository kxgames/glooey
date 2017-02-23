import pyglet
import autoprop

from vecrec import Vector, Rect
from debugtools import p, pp, pv
from . import drawing, containers
from .widget import Widget
from .containers import Deck, Bin, claim_stacked_widgets

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
        self._mouse_state = 'base'
        self._dispatch_rollover_event()
    
    @property
    def is_active(self):
        return self._active_state

    def get_last_rollover_event(self):
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
    custom_predicate = lambda self, w: True

    def __init__(self, clickable, initial_state, predicate=None, **widgets):
        super().__init__(initial_state, **widgets)
        self._predicate = predicate or self.custom_predicate
        clickable.push_handlers(self.on_rollover)

    def on_rollover(self, new_state, old_state):
        if self.is_state_missing(new_state) and new_state == 'down':
            new_state = 'over'

        if self.is_state_missing(new_state) and new_state == 'over':
            new_state = 'base'

        self.set_state(new_state)

    def get_predicate(self):
        return self._predicate

    def set_predicate(self, new_predicate):
        self._predicate = new_predicate

    def is_state_missing(self, state):
        if state not in self.known_states:
            return True
        else:
            widget = self.get_widget(state)
            return not self.predicate(widget)


@autoprop
class PlaceHolder(Clickable):

    def __init__(self, width=0, height=0, color='green', align='fill'):
        super().__init__()
        self.color = drawing.Color.from_anything(color)
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


@autoprop
class EventLogger(PlaceHolder):

    def on_click(self, widget):
        print(f'{self}.on_click(widget={widget})')

    def on_double_click(self, widget):
        print(f'{self}.on_double_click(widget={widget})')

    def on_rollover(self, new_state, old_state):
        print(f'{self}.on_rollover(new_state={new_state}, old_state={old_state})')

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        print(f'{self}.on_mouse_press(x={x}, y={y}, button={button}, modifiers={modifiers})')

    def on_mouse_release(self, x, y, button, modifiers):
        super().on_mouse_release(x, y, button, modifiers)
        print(f'{self}.on_mouse_release(x={x}, y={y}, button={button}, modifiers={modifiers})')

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        print(f'{self}.on_mouse_motion(x={x}, y={y}, dx={dx}, dy={dy})')

    def on_mouse_enter(self, x, y):
        super().on_mouse_enter(x, y)
        print(f'{self}.on_mouse_enter(x={x}, y={y})')

    def on_mouse_leave(self, x, y):
        super().on_mouse_leave(x, y)
        print(f'{self}.on_mouse_leave(x={x}, y={y})')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        print(f'{self}.on_mouse_drag(x={x}, y={y}, dx={dx}, dy={dy}, buttons={buttons}, modifiers={modifiers})')

    def on_mouse_drag_enter(self, x, y):
        super().on_mouse_drag_enter(x, y)
        print(f'{self}.on_mouse_drag_enter(x={x}, y={y})')

    def on_mouse_drag_leave(self, x, y):
        super().on_mouse_drag_leave(x, y)
        print(f'{self}.on_mouse_drag_leave(x={x}, y={y})')

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)
        print(f'{self}.on_mouse_scroll(x={x}, y={y}, scroll_x={scroll_x}, scroll_y={scroll_y})')



@autoprop
class Label(Widget):
    custom_text = ""
    custom_font_name = None
    custom_font_size = None
    custom_bold = None
    custom_italic = None
    custom_underline = None
    custom_kerning = None
    custom_baseline = None
    custom_color = 'green'
    custom_background_color = None
    custom_text_alignment = None
    custom_line_spacing = None

    def __init__(self, text="", line_wrap=None, **style):
        super().__init__()
        self._layout = None
        self._text = text or self.custom_text
        self._line_wrap_width = 0
        self._style = {}
        self.set_style(
                font_name=self.custom_font_name,
                font_size=self.custom_font_size,
                bold=self.custom_bold,
                italic=self.custom_italic,
                underline=self.custom_underline,
                kerning=self.custom_kerning,
                baseline=self.custom_baseline,
                color=self.custom_color,
                background_color=self.custom_background_color,
                align=self.custom_text_alignment,
                line_spacing=self.custom_line_spacing,
        )
        self.set_style(**style)
        if line_wrap:
            self.enable_line_wrap(line_wrap)

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
    custom_image = None
    custom_alignment = 'center'

    def __init__(self, image=None):
        super().__init__()
        self._image = image or self.custom_image
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

    def del_image(self):
        self.set_image(None)


@autoprop
class Background(Widget):
    custom_color = None
    custom_image = None
    custom_center = None
    custom_top = None
    custom_bottom = None
    custom_left = None
    custom_right = None
    custom_top_left = None
    custom_top_right = None
    custom_bottom_left = None
    custom_bottom_right = None
    custom_vtile = 'auto'
    custom_htile = 'auto'

    def __init__(self):
        super().__init__()
        self._artist = drawing.Background(
                color=self.custom_color,
                image=self.custom_image,
                center=self.custom_center,
                top=self.custom_top,
                bottom=self.custom_bottom,
                left=self.custom_left,
                right=self.custom_right,
                top_left=self.custom_top_left,
                top_right=self.custom_top_right,
                bottom_left=self.custom_bottom_left,
                bottom_right=self.custom_bottom_right,
                vtile=self.custom_vtile,
                htile=self.custom_htile,
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

    def set_images(self, *, color=None, image=None, center=None, top=None,
            bottom=None, left=None, right=None, top_left=None, top_right=None,
            bottom_left=None, bottom_right=None, vtile=None, htile=None):

        self._artist.set_images(
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
class Frame(Widget):
    Bin = Bin
    Background = Background
    custom_alignment = 'center'

    def __init__(self):
        super().__init__()

        self._bin = self.Bin()
        self._background = self.Background()

        self._attach_child(self._bin)
        self._attach_child(self._background)

    def do_claim(self):
        return claim_stacked_widgets(self._bin, self._background)

    def do_regroup_children(self):
        self._bin.regroup(pyglet.graphics.OrderedGroup(2, self.group))
        self._background.regroup(pyglet.graphics.OrderedGroup(1, self.group))

    def add(self, child):
        self._bin.add(child)

    def clear(self):
        self._bin.clear()

    def get_bin(self):
        return self._bin

    def get_background(self):
        return self._background


@autoprop
class Button(Clickable):
    Label = Label
    Image = Image
    Base = Background
    Over = Background
    Down = Background
    Off = Background

    custom_label_layer = 3
    custom_image_layer = 2
    custom_background_layer = 1
    custom_alignment = 'center'

    def __init__(self, text='', image=None):
        super().__init__()
        self._stack = containers.Stack()
        self._label = self.Label()
        self._image = self.Image()
        self._backgrounds = {
                'base': self.Base(),
                'over': self.Over(),
                'down': self.Down(),
                'off': self.Off(),
        }
        self._rollover = Rollover(self, 'base', lambda w: not w.is_empty)
        self._rollover.add_states(**self._backgrounds)

        self.set_text(text)
        self.set_image(image)

        self._attach_child(self._stack)
        self._stack.insert(self._label, self.custom_label_layer)
        self._stack.insert(self._image, self.custom_image_layer)
        self._stack.insert(self._rollover, self.custom_background_layer)

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
        self._stack.insert(self._label, self.custom_label_layer)

    def get_image(self):
        return self._image.image

    def set_image(self, image):
        self._image.set_image(image)

    def del_image(self):
        del self._image.image

    def set_background(self, **kwargs):
        for state, widget in self._backgrounds.items():
            widget.set_images(**{
                k.split('_', 1)[1]: v
                for k,v in kwargs.items()
                if k.startswith(state)
            })

    def del_background(self):
        self.set_background()

    def get_base_background(self):
        return self._backgrounds['base']

    def get_over_background(self):
        return self._backgrounds['over']

    def get_base_background(self):
        return self._backgrounds['base']

    def get_off_background(self):
        return self._backgrounds['off']


@autoprop
class Checkbox(Clickable):
    custom_checked_base = None; custom_unchecked_base = None
    custom_checked_over = None; custom_unchecked_over = None
    custom_checked_down = None; custom_unchecked_down = None
    custom_checked_off  = None; custom_unchecked_off  = None
    custom_alignment = 'center'

    def __init__(self, is_checked=False):
        super().__init__()
        self._deck = Deck(is_checked)
        self._attach_child(self._deck)
        self.set_images(
                checked_base=self.custom_checked_base,
                checked_over=self.custom_checked_over,
                checked_down=self.custom_checked_down,
                checked_off=self.custom_checked_off,
                unchecked_base=self.custom_unchecked_base,
                unchecked_over=self.custom_unchecked_over,
                unchecked_down=self.custom_unchecked_down,
                unchecked_off=self.custom_unchecked_off,
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

    def del_images(self):
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


@autoprop
class FillBar(Widget):
    Base = Background
    Fill = Background

    def __init__(self, fraction_filled=0):
        super().__init__()

        self._base = self.Base()
        self._fill = self.Fill()
        self._fill_fraction = fraction_filled
        self._fill_group = None

        self._attach_child(self._base)
        self._attach_child(self._fill)

    def do_claim(self):
        min_width = max(self.base.claimed_width, self.fill.claimed_width)
        min_height = max(self.base.claimed_height, self.fill.claimed_height)
        return min_width, min_height

    def do_resize(self):
        self._update_fill()

    def do_regroup_children(self):
        base_layer = pyglet.graphics.OrderedGroup(1, self.group)
        fill_layer = pyglet.graphics.OrderedGroup(2, self.group)

        self._fill_group = drawing.ScissorGroup(parent=fill_layer)
        self._update_fill()

        self._base.regroup(base_layer)
        self._fill.regroup(self._fill_group)

    def do_draw(self):
        self._update_fill()

    def get_fill(self):
        return self._fill

    def get_base(self):
        return self._base

    def get_fraction_filled(self):
        return self._fill_fraction

    def set_fraction_filled(self, new_fraction):
        self._fill_fraction = new_fraction
        self._update_fill()

    def _update_fill(self):
        if self._fill_group and self.fill.rect:
            self._fill_group.rect = self.fill.rect.copy()
            self._fill_group.rect.width *= self._fill_fraction



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
