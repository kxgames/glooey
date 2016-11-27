import pyglet

from vecrec import Vector, Rect
from pprint import pprint
from . import drawing
from .widget import Widget
from .helpers import late_binding_property

class PlaceHolder (Widget):

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


class EventLogger (PlaceHolder):

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


class Label (Widget):

    def __init__(self, text="", **style):
        super().__init__()
        self._layout = None
        self._document = pyglet.text.decode_text(text)
        self._style = dict(color=drawing.green.tuple)
        self._style.update(style)
        self._line_wrap_width = 0

    def do_claim(self):
        # Make sure the label's text and style are up-to-date before we request 
        # space.  Be careful!  This means that do_draw() can be called before 
        # the widget has self.rect or self.group, which usually cannot happen.
        self.do_draw()

        # Return the amount of space needed to render the label.
        return self._layout.content_width, self._layout.content_height

    def do_draw(self):
        # Any time we need to draw this widget, just delete the underlying 
        # label object and make a new one.  This isn't any slower than keeping 
        # the old object, because all the vertex lists would be redrawn either 
        # way.  And this is more flexible, because it allows us to reset the 
        # batch, the group, and the wrap_lines attribute.
        if self._layout is not None:
            self._document.remove_handlers(self._layout)
            self._layout.delete()

        kwargs = {
                'multiline': True,
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
        if self.rect is not None:
            kwargs['width'] = self.rect.width
            kwargs['height'] = self.rect.height

        self._layout = pyglet.text.layout.TextLayout(self._document, **kwargs)

        # Use begin_update() and end_update() to prevent the layout from 
        # generating new vertex lists until the styles and coordinates have 
        # been set.
        self._layout.begin_update()

        self._document.set_style(0, len(self._document.text), self._style)
        if self.rect is not None:
            self._layout.x = self.rect.bottom_left.x
            self._layout.y = self.rect.bottom_left.y

        self._layout.end_update()

    def do_undraw(self):
        self._layout.delete()

    def get_text(self):
        return self._document.text

    def set_text(self, text):
        self._document = pyglet.text.decode_text(text)
        self.repack()

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
        self.repack()

    def enable_line_wrap(self, width):
        self._line_wrap_width = width

    def disable_line_wrap(self):
        self._line_wrap_width = 0


class Image (Widget):

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
        self._image = new_image
        self.draw()

    image = late_binding_property(get_image, set_image)



# Work in progress...

class Button (Widget):

    def __init__(self):
        super().__init__()
        self._state = 'base'
        self._active = True
        self._children = {}

    def get_state(self):
        if not self._active:
            return 'inactive'
        else:
            return self._state

    def get_possible_states(self):
        return 'base', 'over', 'down', 'inactive'

    def set_state(self, state):
        if state not in self.possible_states:
            raise UsageError("unknown state '{}'".format(state))

        old_state = self.get_state()
        self._state = state
        new_state = self.get_state()

        # Default to the 'base' state if the 'over' or 'down' states are not 
        # defined.
        if new_state not in self._children and new_state in ('over', 'down'):
            new_state = 'base'

        if new_state not in self._children:
            raise UsageError("no widget has been set for the '{}' state".format(state))

        # These could be the same if the 'over' or 'down' states were allowed 
        # to default to the 'base state', if the button is inactive, or if the 
        # user set the state to the same state as before.
        if old_state != new_state:
            self.children[old_state].hide()
            self.children[new_state].show()

    state = property(get_state, set_state)
    possible_states = property(get_possible_states)

    def get_active(self):
        return self._active

    def set_active(self, on_or_off):
        if self._active != self._active:
            self._active = on_or_off
            self.draw()

    active = property(get_active, set_active)

    def toggle_active(self):
        self.active = not self.active

    def reactivate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def set_widget(self, child, state):
        self.children[state] = self._connect_child_widget(child)

    def set_base_widget(self, child):
        self.set_widget(child, 'base')

    def set_over_widget(self, child):
        self.set_widget(child, 'over')

    def set_down_widget(self, child):
        self.set_widget(child, 'down')

    def set_inactive_widget(self, child):
        self.set_widget(child, 'inactive')


    def on_mouse_press(self, x, y, button, modifiers):
        self.set_state('down')

    def on_mouse_release(self, x, y, button, modifiers):
        if self.state == 'down':
            self.dispatch_event('on_click', self)

        self.set_state('over')

    def on_mouse_enter(self, x, y):
        self.set_state('over')

    def on_mouse_leave(self, x, y):
        self.set_state('base')

    def on_mouse_drag_enter(self, x, y):
        pass

    def on_mouse_drag_leave(self, x, y):
        self.set_state('base')


Button.register_event_type('on_click')
Button.register_event_type('on_transition')

class ImageButton (Button):
    """
    A button that's just an image, like an icon.  The button can show different 
    images depending on where the mouse is and whether or not the button is 
    active.
    """

    def __init__(self):
        self.images = {x: Image() for x in self.possible_states}

    def claim(self):
        self.min_width = 0
        self.min_height = 0

        for image in self.images:
            image.claim()

            self.min_width = max(image.min_width, self.min_width)
            self.min_height = max(image.min_height, self.min_height)

    def resize(self, rect):
        super().resize(self, rect)
        for image in self.images:
            image.resize(rect)

    def draw(self):
        self.images[self.state].draw()

    def undraw(self):
        self.images[self.state].undraw()

    def on_transition(self, new_state, old_state):
        self.images[old_state].undraw()
        self.images[new_state].draw()

    def set_image(self, image, state):
        if state in self.images:
            self._detach_child_widget(self.images[state])
        self.images[state] = self._attach_child_widget(Image(image))
        self.repack()

        # Have to remember to repack.  I like this.  Other miscellaneous 
        # widgets have to be aware of when their size might change (i.e. when a 
        # new images is given), so I don't think special support for adding or 
        # removing children is warranted.
        self.images[state] = self.attach_child(child)
        self.repack()

        # Can't think of a good name, would be slightly complicated to write.
        with self.manage_children() as manager:
            manager.attach(child)

        # Really all I want to do:
        self.images[state] = child


        with self.children_manager as cm:

            if state in self.images:
                cm.detach(self.images[state])

            self.images[state] = cm.attach(Image(image))

    def set_base_image(self, image):
        self.set_image(image, 'base')

    def set_over_image(self, image):
        self.set_image(image, 'over')

    def set_down_image(self, image):
        self.set_image(image, 'down')

    def set_inactive_image(self, image):
        self.set_image(image, 'inactive')


class TextButton (Button):

    def set_edge_image(self, state, image, orientation='left', autopad=True):
        self.frames[state].set_edge(image, orientation, autopad)

    def set_edge_image(self, state, image, orientation='left', autopad=True):
        self.frames[state].set_edge(image, orientation, autopad)

    def claim():
        super().claim()

    def set_text(self):
        pass

    def set_font(self):
        pass




