import pyglet

from vecrec import Vector, Rect
from pprint import pprint
from . import drawing
from .widget import Widget
from .containers import place_widget_in_box
from .helpers import late_binding_property

class PlaceHolder(Widget):

    def __init__(self, width=0, height=0, color=drawing.green):
        Widget.__init__(self)
        self.color = color
        self.width = width
        self.height = height
        self.vertex_list = None

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

    def on_mouse_press(self, x, y, button, modifiers):
        message = 'on_mouse_press(x={}, y={}, button={}, modifiers={})'
        print(message.format(x, y, button, modifiers))

    def on_mouse_release(self, x, y, button, modifiers):
        message = 'on_mouse_release(x={}, y={}, button={}, modifiers={})'
        print(message.format(x, y, button, modifiers))

    def on_mouse_motion(self, x, y, dx, dy):
        message = 'on_mouse_motion(x={}, y={}, dx={}, dy={})'
        print(message.format(x, y, dx, dy))

    def on_mouse_enter(self, x, y):
        message = 'on_mouse_enter(x={}, y={})'
        print(message.format(x, y))

    def on_mouse_leave(self, x, y):
        message = 'on_mouse_leave(x={}, y={})'
        print(message.format(x, y))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        message = 'on_mouse_drag(x={}, y={}, dx={}, dy={}, button={}, modifiers={})'
        print(message.format(x, y, dx, dy, buttons, modifiers))

    def on_mouse_drag_enter(self, x, y):
        message = 'on_mouse_drag_enter(x={}, y={})'
        print(message.format(x, y))

    def on_mouse_drag_leave(self, x, y):
        message = 'on_mouse_drag_leave(x={}, y={})'
        print(message.format(x, y))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        message = 'on_mouse_scroll(x={}, y={}, scroll_x={}, scroll_y={})'
        print(message.format(x, y, scroll_x, scroll_y))


class Label(Widget):

    def __init__(self, text="", **style):
        super().__init__()
        self._layout = None
        self._text = text
        self._style = dict(color=drawing.green.tuple)
        self._style.update(style)
        self._line_wrap_width = 0

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
        self._layout.delete()

    def get_text(self):
        return self._text

    def set_text(self, text, width=None):
        self._text = text
        if width is not None:
            self._line_wrap_width = width
        self.repack(force=True)

    text = late_binding_property(get_text, set_text)

    def get_font_name(self):
        return self.get_style('font_name')

    def set_font_name(self, name):
        self.set_style(font_name=name)

    font_name = late_binding_property(get_font_name, set_font_name)

    def get_font_size(self):
        return self.get_style('font_size')

    def set_font_size(self, size):
        self.set_style(font_size=size)

    font_size = late_binding_property(get_font_size, set_font_size)

    def get_bold(self):
        return self.get_style('bold')

    def set_bold(self, bold):
        self.set_style(bold=bold)

    bold = late_binding_property(get_bold, set_bold)

    def get_italic(self):
        return self.get_style('italic')

    def set_italic(self, italic):
        self.set_style(italic=italic)

    italic = late_binding_property(get_italic, set_italic)

    def get_underline(self):
        return self.get_style('underline')

    def set_underline(self, underline):
        if underline:
            self.set_style(underline=self.color)
        else:
            self.set_style(underline=None)

    underline = late_binding_property(get_underline, set_underline)

    def get_kerning(self):
        return self.get_style('kerning')

    def set_kerning(self, kerning):
        self.set_style(kerning=kerning)

    kerning = late_binding_property(get_kerning, set_kerning)

    def get_baseline(self):
        return self.get_style('baseline')

    def set_baseline(self, baseline):
        self.set_style(baseline=baseline)

    baseline = late_binding_property(get_baseline, set_baseline)

    def get_color(self):
        return self.get_style('color')

    def set_color(self, color):
        if isinstance(color, str):
            color = drawing.colors[color]
        if hasattr(color, 'tuple'):
            color = color.tuple

        # I want the underline attribute to behave as a boolean, but in the 
        # TextLayout API it's a color.  So when the color changes, I have to 
        # update the underline (if it's been set).
        style = {'color': color}
        if self.underline is not None:
            style['underline'] = color
        self.set_style(**style)

    color = late_binding_property(get_color, set_color)

    def get_bg_color(self):
        return self.get_style('background_color')

    def set_bg_color(self, color):
        if isinstance(color, str):
            color = drawing.colors[color]
        if hasattr(color, 'tuple'):
            color = color.tuple
        self.set_style(background_color=color)

    bg_color = late_binding_property(get_bg_color, set_bg_color)

    def get_alignment(self):
        return self.get_style('alignment')

    def set_alignment(self, alignment):
        self.set_style(align=alignment)

    alignment = late_binding_property(get_alignment, set_alignment)

    def get_line_spacing(self):
        return self.get_style('line_spacing')

    def set_line_spacing(self, spacing):
        self.set_style(line_spacing=spacing)

    line_spacing = late_binding_property(get_line_spacing, set_line_spacing)

    def get_style(self, style):
        return self._style.get(style)

    def set_style(self, **style):
        self._style.update(style)
        self.repack(force=True)

    def enable_line_wrap(self, width):
        self._line_wrap_width = width
        self.repack(force=True)

    def disable_line_wrap(self):
        self.enable_line_wrap(0)


class Image(Widget):

    def __init__(self, image=None):
        super().__init__()
        self._image = image
        self._sprite = None

    def do_claim(self):
        return self.image.width, self.image.height

    def do_regroup(self):
        if self._sprite is not None:
            self._sprite.group = group

    def do_draw(self):
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

    def get_image(self):
        return self._image

    def set_image(self, new_image):
        if self._image is not new_image:
            self._image = new_image
            self.repack(force=True)

    image = late_binding_property(get_image, set_image)


class Button(Widget):

    def __init__(self, text=""):
        super().__init__()
        self._states = {}
        self._mouse = 'base'
        self._active = True
        self._label = Label(text)
        self._label_placement = 'center'
        self._background = Image()
        self._background_placement = 'center'
        self._attach_child(self._label)
        self._attach_child(self._background)

    def reactivate(self):
        self._active = True
        self._update_state()

    def deactivate(self):
        self._active = False
        self._update_state()

    def do_claim(self):
        min_width = max(self._label.min_width, self._background.min_width)
        min_height = max(self._label.min_height, self._background.min_height)
        return min_width, min_height

    def do_regroup_children(self):
        self._background.regroup(pyglet.graphics.OrderedGroup(0, self.group))
        self._label.regroup(pyglet.graphics.OrderedGroup(1, self.group))

    def do_resize_children(self):
        place_widget_in_box(self._label, self.rect, self._label_placement)
        place_widget_in_box(self._background, self.rect, self._background_placement)

    def on_mouse_press(self, x, y, button, modifiers):
        self._mouse = 'down'
        self._update_state()

    def on_mouse_release(self, x, y, button, modifiers):
        if self._active and self._mouse == 'down':
            self.dispatch_event('on_click', self)

        self._mouse = 'over'
        self._update_state()

    def on_mouse_enter(self, x, y):
        self._mouse = 'over'
        self._update_state()

    def on_mouse_leave(self, x, y):
        self._mouse = 'base'
        self._update_state()

    def on_mouse_drag_enter(self, x, y):
        pass

    def on_mouse_drag_leave(self, x, y):
        self._mouse = 'base'
        self._update_state()

    @property
    def is_active(self):
        return self._active

    def get_state(self):
        state = self._mouse

        if state not in self._states and state == 'down':
            state = 'over'

        if state not in self._states and state == 'over':
            state = 'base'

        if not self._active:
            state = 'inactive'

        return state

    state = late_binding_property(get_state)

    def get_image(self, state=None):
        if state is None: state = self.get_state()
        return self._states.get(state)

    image = late_binding_property(get_image)

    def set_image(self, state, image):
        self._states[state] = image
        if self._mouse == state:
            self._background.image = image

    def get_base_image(self, image):
        self.get_image('base', image)

    def set_base_image(self, image):
        self.set_image('base', image)

    base_image = late_binding_property(get_base_image, set_base_image)

    def get_over_image(self, image):
        self.get_image('over', image)

    def set_over_image(self, image):
        self.set_image('over', image)

    over_image = late_binding_property(get_over_image, set_over_image)

    def get_down_image(self, image):
        self.get_image('down', image)

    def set_down_image(self, image):
        self.set_image('down', image)

    down_image = late_binding_property(get_down_image, set_down_image)

    def get_inactive_image(self, image):
        self.get_image('inactive', image)

    def set_inactive_image(self, image):
        self.set_image('inactive', image)

    inactive_image = late_binding_property(get_inactive_image, set_inactive_image)

    def get_label(self):
        return self._label

    label = late_binding_property(get_label)

    def get_text(self):
        return self._label.text

    def set_text(self, text):
        self._label.text = text

    text = late_binding_property(get_text, set_text)

    def get_label_placement(self, new_placement):
        return self._label_placement

    def set_label_placement(self, new_placement):
        self._label_placement = new_placement
        self.repack()

    label_placement = late_binding_property(get_label_placement, set_label_placement)

    def get_image_placement(self, new_placement):
        return self._background_placement

    def set_image_placement(self, new_placement):
        self._background_placement = new_placement
        self.repack()

    image_placement = late_binding_property(get_image_placement, set_image_placement)

    def _update_state(self):
        state = self.get_state()
        if state not in self._states:
            raise ValueError("no images for '{}' state".format(state))
        self._background.image = self._states[state]


Button.register_event_type('on_click')

class Checkbox(Widget):

    def __init__(self):
        super().__init__()
        self._image = Image()
        self._attach_child(self._image)

        # self._states is a 2D dictionary of images representing the various 
        # states the checkbox can be in.  The first index represents whether or 
        # not the box is check or not, and can be either True of False.  The 
        # second index represented the state of the mouse and can be either 
        # 'base', 'over', 'down', 'inactive'.
        self._states = {True: {}, False: {}}

        # These variables keep track of the state of the checkbox.  Whether or 
        # not the widget is active is tracked separately from the mouse, even 
        # though they're considered together in self._states, so that the mouse 
        # state will be up-to-date when the widget is reactivated.
        self._checked = False
        self._mouse = 'base'
        self._active = True

    def check(self):
        if not self._checked:
            self.toggle()

    def uncheck(self):
        if self._checked:
            self.toggle()

    def toggle(self):
        self._checked = not self._checked
        self.dispatch_event('on_toggle', self)
        self._update_state()

    def reactivate(self):
        self._active = True
        self._update_state()

    def deactivate(self):
        self._active = False
        self._update_state()

    def do_claim(self):
        return self._image.min_width, self._image.min_height

    def do_resize_children(self):
        self._image.resize(self.rect)

    def on_mouse_press(self, x, y, button, modifiers):
        self._mouse = 'down'
        self._update_state()

    def on_mouse_release(self, x, y, button, modifiers):
        if self._active and self._mouse == 'down':
            self.toggle()

        self._mouse = 'over'
        self._update_state()

    def on_mouse_enter(self, x, y):
        self._mouse = 'over'
        self._update_state()

    def on_mouse_leave(self, x, y):
        self._mouse = 'base'
        self._update_state()

    def on_mouse_drag_enter(self, x, y):
        pass

    def on_mouse_drag_leave(self, x, y):
        self._mouse = 'base'
        self._update_state()

    @property
    def is_checked(self):
        return self._checked

    @property
    def is_active(self):
        return self._active

    def get_state(self):
        checked_state = self._checked
        mouse_state = self._mouse

        if mouse_state == 'down' and 'down' not in self._states[checked_state]:
            mouse_state = 'over'

        if mouse_state == 'over' and 'over' not in self._states[checked_state]:
            mouse_state = 'base'

        if not self._active:
            mouse_state = 'inactive'

        return checked_state, mouse_state

    state = late_binding_property(get_state)
        
    def get_image(self, is_checked=None, mouse_state=None):
        if is_checked is None and mouse_state is None:
            is_checked, mouse_state = self.get_state()
        return self._states[is_checked].get(mouse_state)

    image = late_binding_property(get_image)

    def set_image(self, is_checked, mouse_state, image):
        self._states[is_checked][mouse_state] = image
        if (is_checked, mouse_state) == self.get_state():
            self._image.image = image

    def get_base_checked_image(self):
        return self.get_image(True, 'base')

    def set_base_checked_image(self, image):
        self.set_image(True, 'base', image)

    base_checked_image = late_binding_property(
            get_base_checked_image, set_base_checked_image)

    def get_base_unchecked_image(self):
        return self.get_image(False, 'base')

    def set_base_unchecked_image(self, image):
        self.set_image(False, 'base', image)

    base_unchecked_image = late_binding_property(
            get_base_unchecked_image, set_base_unchecked_image)

    def get_over_checked_image(self):
        return self.get_image(True, 'over')

    def set_over_checked_image(self, image):
        self.set_image(True, 'over', image)

    over_checked_image = late_binding_property(
            get_over_checked_image, set_over_checked_image)

    def get_over_unchecked_image(self):
        return self.get_image(False, 'over')

    def set_over_unchecked_image(self, image):
        self.set_image(False, 'over', image)

    over_unchecked_image = late_binding_property(
            get_over_unchecked_image, set_over_unchecked_image)

    def get_down_checked_image(self):
        return self.get_image(True, 'down')

    def set_down_checked_image(self, image):
        self.set_image(True, 'down', image)

    down_checked_image = late_binding_property(
            get_down_checked_image, set_down_checked_image)

    def get_down_unchecked_image(self):
        return self.get_image(False, 'down')

    def set_down_unchecked_image(self, image):
        self.set_image(False, 'down', image)

    down_unchecked_image = late_binding_property(
            get_down_unchecked_image, set_down_unchecked_image)

    def get_inactive_checked_image(self):
        return self.get_image(True, 'inactive')

    def set_inactive_checked_image(self, image):
        self.set_image(True, 'inactive', image)

    inactive_checked_image = late_binding_property(
            get_inactive_checked_image, set_inactive_checked_image)

    def get_inactive_unchecked_image(self):
        return self.get_image(False, 'inactive')

    def set_inactive_unchecked_image(self, image):
        self.set_image(False, 'inactive', image)

    inactive_unchecked_image = late_binding_property(
            get_inactive_unchecked_image, set_inactive_unchecked_image)

    def _update_state(self):
        checked_state, mouse_state = self.get_state()
        if mouse_state not in self._states[checked_state]:
            raise ValueError("no images for the '{}_{}' state".format(
                mouse_state, 'checked' if checked_state else 'unchecked'))
        self._image.image = self.get_image(checked_state, mouse_state)


Checkbox.register_event_type('on_toggle')

class RadioButton(Checkbox):

    def __init__(self, peers=None):
        super().__init__()
        if peers is not None:
            self.peers = peers

    def on_toggle(self, widget):
        if self.is_checked:
            for peer in self.peers:
                if peer is not self:
                    peer.uncheck()


