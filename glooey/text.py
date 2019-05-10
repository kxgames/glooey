#!/usr/bin/env python3

"""
Widgets that can display and input text.
"""

import pyglet
import autoprop

from vecrec import Vector, Rect
from glooey import drawing
from glooey.widget import Widget
from glooey.images import Background
from glooey.containers import Stack, Deck
from glooey.helpers import *

@autoprop
@register_event_type('on_edit_text')
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

    def __init__(self, text=None, line_wrap=None, **style):
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

    def __repr__(self):
        import textwrap

        repr = '{cls}(id={id}, "{text}")'
        args = {
                'cls': self.__class__.__name__,
                'id': hex(id(self))[-4:],
        }
        try:
            args['text'] = textwrap.shorten(self.text, width=10, placeholder='...')
        except:
            repr = '{cls}(id={id})'

        return repr.format(**args)

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
        # Usually self.rect is guaranteed to be set by the time this method is 
        # called, but that is not the case for this widget.  The do_claim() 
        # method needs to call do_draw() to see how much space the text will 
        # need, and that happens before self.rect is set (since it's part of 
        # the process of setting self.rect). 
        if not ignore_rect:
            kwargs['width'] = self.rect.width
            kwargs['height'] = self.rect.height

        # Enable line wrapping, if the user requested it.  The width of the 
        # label is set to the value given by the user when line-wrapping was 
        # enabled.  This is done after the size of the assigned rect is 
        # considered, so the text will wrap at the specified line width no 
        # matter how much space is available to it.  This ensures that the text 
        # takes up all of the height it requested.  It would be better if the 
        # text could update its height claim after knowing how much width it 
        # got, but that's a non-trivial change.
        if self._line_wrap_width:
            kwargs['width'] = self._line_wrap_width
            kwargs['wrap_lines'] = True
        
        # It's best to make a fresh document each time.  Previously I was 
        # storing the document as a member variable, but I ran into corner 
        # cases where the document would have an old style that wouldn't be 
        # compatible with the new TextLayout (specifically 'align' != 'left' if 
        # line wrapping is no loner enabled).
        document = pyglet.text.decode_text(self._text)
        document.push_handlers(self.on_insert_text, self.on_delete_text)

        if self._layout:
            self._layout.delete()
        self._layout = self.do_make_new_layout(document, kwargs)

        # Use begin_update() and end_update() to prevent the layout from 
        # generating new vertex lists until the styles and coordinates have 
        # been set.
        self._layout.begin_update()

        # The layout will crash if it doesn't have an explicit width and the 
        # style specifies an alignment.
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

    def do_make_new_layout(self, document, kwargs):
        return pyglet.text.layout.TextLayout(document, **kwargs)

    def on_insert_text(self, start, text):
        self._text = self._layout.document.text
        self.dispatch_event('on_edit_text', self)

    def on_delete_text(self, start, end):
        self._text = self._layout.document.text
        self.dispatch_event('on_edit_text', self)

    def get_text(self):
        return self._layout.document.text

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
        self._repack()

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

        self._repack()


@autoprop
@register_event_type('on_focus')
@register_event_type('on_unfocus')
class EditableLabel(Label):
    custom_selection_color = 'black'
    custom_selection_background_color = None
    custom_unfocus_on_enter = True

    def __init__(self, text="", line_wrap=None, **style):
        super().__init__(text, line_wrap, **style)
        self._caret = None
        self._focus = False
        self._is_mouse_over = False
        self._unfocus_on_enter = self.custom_unfocus_on_enter

        # I'm surprised pyglet doesn't treat the selection colors like all the 
        # other styles.  Instead they're attributes of IncrementalTextLayout.
        self._selection_color = self.custom_selection_color
        self._selection_background_color = self.custom_selection_background_color

    def do_claim(self):
        font = pyglet.font.load(self.font_name)
        min_size = font.ascent - font.descent
        return min_size, min_size

    def focus(self):
        # Push handlers directly to the window, so even if the user has 
        # attached their own handlers (e.g. for hotkeys) above the GUI, the 
        # form will still take focus.

        if not self._focus:
            self._focus = True
            self._caret.on_activate()
            self.window.push_handlers(self._caret)
            self.window.push_handlers(
                    on_mouse_press=self.on_window_mouse_press,
                    on_key_press=self.on_window_key_press,
                    on_key_release=self.on_window_key_release,
            )
            self.dispatch_event('on_focus', self)

    def unfocus(self):
        if self._focus:
            self._focus = False
            self._caret.on_deactivate()
            self._layout.set_selection(0,0)
            self.window.remove_handlers(self._caret)
            self.window.remove_handlers(
                    on_mouse_press=self.on_window_mouse_press,
                    on_key_press=self.on_window_key_press,
                    on_key_release=self.on_window_key_release,
            )
            self.dispatch_event('on_unfocus', self)

    def on_mouse_enter(self, x, y):
        super().on_mouse_enter(x, y)
        self._is_mouse_over = True

    def on_mouse_leave(self, x, y):
        super().on_mouse_leave(x, y)
        self._is_mouse_over = False

    def on_mouse_press(self, x, y, button, modifiers):
        if not self._focus:
            self.focus()
            self._caret.on_mouse_press(x, y, button, modifiers)

    def on_window_mouse_press(self, x, y, button, modifiers):
        # Determine if the mouse is over the form by tracking mouse enter and 
        # leave events.  This is more robust than checking the mouse 
        # coordinates in this method, because it still works when the form has 
        # a parent that changes its coordinates, like a ScrollBox.

        if not self._is_mouse_over:
            self.unfocus()

            # This event will get swallowed by the caret, so dispatch a new 
            # event after the caret handlers have been popped.

            self.window.dispatch_event('on_mouse_press', x, y, button, modifiers)
    
    def on_window_key_press(self, symbol, modifiers):
        if self._unfocus_on_enter and symbol == pyglet.window.key.ENTER:
            self.unfocus()
        return True

    def on_window_key_release(self, symbol, modifiers):
        return True

    def do_make_new_layout(self, document, kwargs):
        # Make a new layout (optimized for editing).
        new_layout = pyglet.text.layout.IncrementalTextLayout(document, **kwargs)

        new_layout.selection_color = drawing.Color.from_anything(
                self._selection_color).tuple
        new_layout.selection_background_color = drawing.Color.from_anything(
                self._selection_background_color or self.color).tuple

        # If the previous layout had a selection, keep it.  Note that the 
        # normal text layout doesn't have the concept of a selection, so 
        # this logic needs to be here rather than in the base class.
        if self._layout:
            new_layout.set_selection(
                    self._layout._selection_start, 
                    self._layout._selection_end, 
            )

        # Make a new caret.
        new_caret = pyglet.text.caret.Caret(new_layout, color=self.color[:3])

        # Keep the caret in the same place as it was before, and clean up the 
        # old caret object.
        if self._caret:
            new_caret.position = self._caret.position
            new_caret.mark = self._caret.mark

            self.window.remove_handlers(self._caret)
            self._caret.delete()

        # Match the caret's behavior to the widget's current focus state.
        if self._focus:
            new_caret.on_activate()
            self.window.push_handlers(new_caret)
        else:
            new_caret.on_deactivate()

        self._caret = new_caret
        return new_layout

    def get_selection_color(self):
        return self._selection_color

    def set_selection_color(self, new_color):
        self._selection_color = new_color
        self._draw()

    def get_selection_background_color(self):
        return self._selection_background_color

    def set_selection_background_color(self, new_color):
        self._selection_background_color = new_color
        self._draw()

    def get_unfocus_on_enter(self):
        return self._unfocus_on_enter

    def set_unfocus_on_enter(self, new_behavior):
        self._unfocus_on_enter = new_behavior


@autoprop
class Form(Widget):
    Label = EditableLabel
    Base = Background
    Focused = None
    Deck = Deck

    def __init__(self, text=""):
        super().__init__()

        self._stack = Stack()

        self._label = self.Label(text)
        self._label.push_handlers(
                on_focus=lambda w: self.dispatch_event('on_focus', self),
                on_unfocus=lambda w: self.dispatch_event('on_unfocus', self),
        )

        # If there are two backgrounds, create a deck to switch between them.  
        # Otherwise skip the extra layer of hierarchy.
        if self.Focused is None:
            self._bg = self.Base()

        else:
            self._bg = self.Deck('base')
            self._bg.add_states(
                    base=self.Base(),
                    focused=self.Focused(),
            )
            self._label.push_handlers(
                    on_focus=lambda w: self._bg.set_state('focused'),
                    on_unfocus=lambda w: self._bg.set_state('base'),
            )

        self._stack.add_front(self._label)
        self._stack.add_back(self._bg)
        self._attach_child(self._stack)

    def get_label(self):
        return self._label

    def get_text(self):
        return self._label.text

    def set_text(self, new_text):
        self._label.text = new_text


