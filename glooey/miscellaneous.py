import pyglet

from vecrec import Vector, Rect
from .widget import Widget
from . import drawing

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

    def __init__(self, text='', **style):
        super().__init__()
        self.document = pyglet.text.document.UnformattedDocument(text)

        # Make the text white by default, so it will show up against the black 
        # default background.

        self.set_color('white')
        self.set_style(**style)
        self.layout = pyglet.text.layout.TextLayout(
                self.document,
                width=0, height=0, multiline=True, wrap_lines=False)

    def set_text(self, text):
        self.document.text = text

    def set_font_name(self, name):
        self.set_style(font_name=name)

    def set_font_size(self, size):
        self.set_style(font_size=size)

    def set_bold(self, bold):
        self.set_style(bold=bold)

    def set_italic(self, italic):
        self.set_style(italic=italic)

    def set_underline(self, underline):
        self.set_style(underline=underline)

    def set_kerning(self, kerning):
        self.set_style(kerning=kerning)

    def set_baseline(self, baseline):
        self.set_style(baseline=baseline)

    def set_color(self, color):
        if isinstance(color, str):
            color = drawing.colors[color]
        if hasattr(color, 'tuple'):
            color = color.tuple
        self.set_style(color=color)

    def set_bg_color(self, color):
        if isinstance(color, str):
            color = drawing.colors[color]
        if hasattr(color, 'tuple'):
            color = color.tuple
        self.set_style(background_color=color)

    def set_alignment(self, alignment):
        self.set_style(align=alignment)

    def set_line_spacing(self, spacing):
        self.set_style(line_spacing=spacing)

    def enable_line_wrap(self, width):
        self.layout._wrap_lines_flag = True
        sellf.min_line_width = width

    def disable_line_wrap(self):
        self.layout._wrap_lines_flag = False
        self.min_width = 0

    def set_style(self, **style):
        self.document.set_style(0, len(self.document.text), style)

    def do_claim(self):
        """
        Request enough space to render the text.
        """
        self.layout.width = self.min_line_width

        min_width = max(self.min_width, self.layout.content_width)
        min_height = max(self.min_height, self.layout.content_height)

        return min_width, min_height

    def do_draw(self):
        self.layout.x = self.rect.left
        self.layout.y = self.rect.bottom
        self.layout.width = self.rect.width
        self.layout.height = self.rect.height
        self.layout.batch = self.batch
        self.layout.group = self.group

    def do_undraw(self):
        self.layout.delete()


class Image (Widget):

    def __init__(self, image=None):
        self.image = image

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

    def do_claim(self):
        image = self.get_image()
        return image.width, image.height

    def do_regroup(self):
        if self.sprite is not None:
            self.sprite.group = group

    def do_draw(self):
        image = self.get_image()

        if self.sprite is None:
            self.sprite = pyglet.sprite.Sprite(
                    image, batch=self.batch, group=self.group)
        else:
            self.sprite.image = image

        self.sprite.x = self.rect.left
        self.sprite.y = self.rect.bottom

    def do_undraw(self):
        if self.sprite is not None:
            self.sprite.delete()



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




