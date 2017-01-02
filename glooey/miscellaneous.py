import pyglet
import autoprop

from vecrec import Vector, Rect
from pprint import pprint
from . import drawing
from .widget import Widget
from .containers import place_widget_in_box

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


@autoprop
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
        if self._layout is not None:
            self._layout.delete()

    def get_text(self):
        return self._text

    def set_text(self, text, width=None):
        self._text = text
        if width is not None:
            self._line_wrap_width = width
        self.repack(force=True)

    def get_font_name(self):
        return self.get_style('font_name')

    def set_font_name(self, name):
        self.set_style(font_name=name)

    def get_font_size(self):
        return self.get_style('font_size')

    def set_font_size(self, size):
        self.set_style(font_size=size)

    def get_bold(self):
        return self.get_style('bold')

    def set_bold(self, bold):
        self.set_style(bold=bold)

    def get_italic(self):
        return self.get_style('italic')

    def set_italic(self, italic):
        self.set_style(italic=italic)

    def get_underline(self):
        return self.get_style('underline')

    def set_underline(self, underline):
        if underline:
            self.set_style(underline=self.color)
        else:
            self.set_style(underline=None)

    def get_kerning(self):
        return self.get_style('kerning')

    def set_kerning(self, kerning):
        self.set_style(kerning=kerning)

    def get_baseline(self):
        return self.get_style('baseline')

    def set_baseline(self, baseline):
        self.set_style(baseline=baseline)

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

    def get_bg_color(self):
        return self.get_style('background_color')

    def set_bg_color(self, color):
        if isinstance(color, str):
            color = drawing.colors[color]
        if hasattr(color, 'tuple'):
            color = color.tuple
        self.set_style(background_color=color)

    def get_alignment(self):
        return self.get_style('alignment')

    def set_alignment(self, alignment):
        self.set_style(align=alignment)

    def get_line_spacing(self):
        return self.get_style('line_spacing')

    def set_line_spacing(self, spacing):
        self.set_style(line_spacing=spacing)

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


@autoprop
class Image(Widget):

    def __init__(self, image=None):
        super().__init__()
        self._image = image
        self._sprite = None

    def do_claim(self):
        if self.image:
            return self.image.width, self.image.height
        else:
            return 0, 0

    def do_regroup(self):
        if self._sprite is not None:
            self._sprite.group = group

    @autoprop
    def do_draw(self):
        if not self.image:
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

    def get_image(self):
        return self._image

    def set_image(self, new_image):
        if self._image is not new_image:
            self._image = new_image
            self.repack(force=True)


@autoprop
class Background(Widget):

    def __init__(self, *, color=None, center=None, top=None, bottom=None, 
            left=None, right=None, top_left=None, top_right=None, 
            bottom_left=None, bottom_right=None, vtile=False, htile=False):

        super().__init__()
        self._artist = drawing.Background(
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
        self.repack(force=True)

    def set_image(self, image):
        self._artist.set_image(image)
        self.repack(force=True)


@autoprop
class Button(Widget):

    LabelClass = Label
    IconClass = Image
    BackgroundClass = Background

    def __init__(self, text=""):
        super().__init__()
        self._mouse = 'base'
        self._active = True
        self._current_state = 'base'
        self._previous_state = 'base'
        self._configured_states = set()
        self._label = self.LabelClass(text)
        self._label_placement = 'center'
        self._icon = self.IconClass()
        self._icon_placement = 'center'
        self._backgrounds = {
                state: self.BackgroundClass()
                for state in self.possible_states}
        self._background_placement = 'center'

        self._attach_child(self._label)
        self._attach_child(self._icon)
        for state, bg in self._backgrounds.items():
            self._attach_child(bg)
            if state != self._current_state:
                bg.hide()


    def deactivate(self):
        if self._active:
            self._active = False
            self._update_state()

    def reactivate(self):
        if not self._active:
            self._active = True
            self._update_state()

    def do_claim(self):
        min_width = max(
                self._label.min_width,
                self._icon.min_width,
                *(bg.min_width for bg in self._backgrounds.values()),
        )
        min_height = max(
                self._label.min_height,
                self._icon.min_height,
                *(bg.min_height for bg in self._backgrounds.values()),
        )
        return min_width, min_height

    def do_regroup_children(self):
        self._label.regroup(pyglet.graphics.OrderedGroup(2, self.group))
        self._icon.regroup(pyglet.graphics.OrderedGroup(1, self.group))
        for bg in self._backgrounds.values():
            bg.regroup(pyglet.graphics.OrderedGroup(0, self.group))

    def do_resize_children(self):
        place_widget_in_box(self._label, self.rect, self._label_placement)
        place_widget_in_box(self._icon, self.rect, self._icon_placement)
        for bg in self._backgrounds.values():
            place_widget_in_box(bg, self.rect, self._background_placement)

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
        return self._current_state

    def get_previous_state(self):
        return self._previous_state

    def get_possible_states(self):
        return 'base', 'over', 'down', 'inactive'

    def get_text(self):
        return self._label.text

    def set_text(self, text):
        self._label.text = text

    def get_label(self):
        return self._label

    def get_label_placement(self, new_placement):
        return self._label_placement

    def set_label_placement(self, new_placement):
        self._label_placement = new_placement
        self.repack()

    def get_icon(self):
        return self._icon.image

    def set_icon(self, image):
        self._icon.image = image
        
    def get_icon_placement(self, new_placement):
        return self._icon_placement

    def set_icon_placement(self, new_placement):
        self._icon_placement = new_placement
        self.repack()

    def get_base_background(self):
        return self._backgrounds['base'].get_images()

    def set_base_background(self, **kwargs):
        self._configured_states.add('base')
        self._backgrounds['base'].set_images(**kwargs)

    def set_base_image(self, image):
        self._configured_states.add('base')
        self._backgrounds['base'].set_image(image)

    def del_base_background(self):
        self._configured_states.discard('base')

    def get_over_background(self):
        return self._backgrounds['over'].get_images()

    def set_over_background(self, **kwargs):
        self._configured_states.add('over')
        self._backgrounds['over'].set_images(**kwargs)

    def set_over_image(self, image):
        self._configured_states.add('over')
        self._backgrounds['over'].set_image(image)

    def del_over_background(self):
        self._configured_states.discard('over')

    def get_down_background(self):
        return self._backgrounds['down'].get_images()

    def set_down_background(self, **kwargs):
        self._configured_states.add('down')
        self._backgrounds['down'].set_images(**kwargs)

    def set_down_image(self, image):
        self._configured_states.add('down')
        self._backgrounds['down'].set_image(image)

    def del_down_background(self):
        self._configured_states.discard('down')

    def get_inactive_background(self):
        return self._backgrounds['inactive'].get_images()

    def set_inactive_background(self, **kwargs):
        self._configured_states.add('inactive')
        self._backgrounds['inactive'].set_images(**kwargs)

    def set_inactive_image(self, image):
        self._configured_states.add('inactive')
        self._backgrounds['inactive'].set_image(image)

    def del_inactive_background(self):
        self._configured_states.discard('inactive')

    def get_background_placement(self, new_placement):
        return self._background_placement

    def set_background_placement(self, new_placement):
        self._background_placement = new_placement
        self.repack()

    def _update_state(self):
        new_state = self._mouse

        if new_state not in self._configured_states and new_state == 'down':
            new_state = 'over'

        if new_state not in self._configured_states and new_state == 'over':
            new_state = 'base'

        if not self._active:
            new_state = 'inactive'

        if new_state not in self._configured_states:
            raise ValueError(f"no images for '{new_state}' state")

        assert new_state in self.possible_states
        self._previous_state = self._current_state
        self._current_state = new_state

        if self._current_state != self._previous_state:
            self._backgrounds[self._previous_state].hide()
            self._backgrounds[self._current_state].unhide()
            self.repack()

Button.register_event_type('on_click')


@autoprop
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

    def get_image(self, is_checked=None, mouse_state=None):
        if is_checked is None and mouse_state is None:
            is_checked, mouse_state = self.get_state()
        return self._states[is_checked].get(mouse_state)

    def set_image(self, is_checked, mouse_state, image):
        self._states[is_checked][mouse_state] = image
        if (is_checked, mouse_state) == self.get_state():
            self._image.image = image

    def get_base_checked_image(self):
        return self.get_image(True, 'base')

    def set_base_checked_image(self, image):
        self.set_image(True, 'base', image)

    def get_base_unchecked_image(self):
        return self.get_image(False, 'base')

    def set_base_unchecked_image(self, image):
        self.set_image(False, 'base', image)

    def get_over_checked_image(self):
        return self.get_image(True, 'over')

    def set_over_checked_image(self, image):
        self.set_image(True, 'over', image)

    def get_over_unchecked_image(self):
        return self.get_image(False, 'over')

    def set_over_unchecked_image(self, image):
        self.set_image(False, 'over', image)

    def get_down_checked_image(self):
        return self.get_image(True, 'down')

    def set_down_checked_image(self, image):
        self.set_image(True, 'down', image)

    def get_down_unchecked_image(self):
        return self.get_image(False, 'down')

    def set_down_unchecked_image(self, image):
        self.set_image(False, 'down', image)

    def get_inactive_checked_image(self):
        return self.get_image(True, 'inactive')

    def set_inactive_checked_image(self, image):
        self.set_image(True, 'inactive', image)

    def get_inactive_unchecked_image(self):
        return self.get_image(False, 'inactive')

    def set_inactive_unchecked_image(self, image):
        self.set_image(False, 'inactive', image)

    def _update_state(self):
        checked_state, mouse_state = self.get_state()
        if mouse_state not in self._states[checked_state]:
            raise ValueError("no images for the '{}_{}' state".format(
                mouse_state, 'checked' if checked_state else 'unchecked'))
        self._image.image = self.get_image(checked_state, mouse_state)


Checkbox.register_event_type('on_toggle')

@autoprop
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
