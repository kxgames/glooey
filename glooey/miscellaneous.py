import pyglet

from vecrec import Vector, Rect
from .widget import Widget
from . import drawing

class PlaceHolder (Widget):

    def __init__(self, width=0, height=0, color=drawing.green):
        Widget.__init__(self)
        self.color = color
        self.min_width = width
        self.min_height = height
        self.vertex_list = None

    def draw(self):
        top_left = self.rect.top_left
        top_right = self.rect.top_right
        bottom_left = self.rect.bottom_left
        bottom_right = self.rect.bottom_right

        # Originally I used GL_LINE_STRIP, but I couldn't figure out how to 
        # stop the place holders from connecting to each other (i.e. I couldn't 
        # figure out how to break the line strip).  Now I'm just using GL_LINES 
        # instead.

        vertices = (
                # the outline
                bottom_left.tuple + bottom_right.tuple + 
                bottom_right.tuple + top_right.tuple + 
                top_right.tuple + top_left.tuple + 
                top_left.tuple + bottom_left.tuple + 

                # the cross
                bottom_left.tuple + top_right.tuple + 
                bottom_right.tuple + top_left.tuple
        ) 

        self.vertex_list = self.batch.add(
                12, pyglet.gl.GL_LINES, self.group,
                ('v2f', vertices),
                ('c4B', 12 * self.color.tuple))

    def undraw(self):
        if self.vertex_list:
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
    pass

class Button (Widget):

    # The images should all be the same size.  This isn't checked, but things 
    # won't act right if violated.

    def __init__(self):
        super(Button, self).__init__()
        #self.state_stack = []
        self.state = 'base'
        self.images = {}
        self.sprite = None

    def set_base_image(self, image):
        self.images['base'] = image

    def set_over_image(self, image):
        self.images['over'] = image

    def set_down_image(self, image):
        self.images['down'] = image

    def get_image(self, state=None):
        if state is None: state = self.state
        try: return self.images[state]
        except KeyError: raise ValueError("No image specified for '{}' button state".format(self.state))


    def claim(self):
        image = self.get_image()
        self.min_width = image.width
        self.min_height = image.height

    def draw(self):
        image = self.get_image()

        if self.sprite is None:
            self.sprite = pyglet.sprite.Sprite(
                    image, batch=self.batch, group=self.group)
        else:
            self.sprite.image = image

        self.sprite.x = self.rect.left
        self.sprite.y = self.rect.bottom

    def undraw(self):
        if self.sprite is not None:
            self.sprite.delete()


    def on_mouse_press(self, x, y, button, modifiers):
        self.state = 'down'
        self.draw()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.state == 'down':
            self.dispatch_event('on_click', self)

        self.state = 'over'
        self.draw()

    def on_mouse_enter(self, x, y):
        self.state = 'over'
        self.draw()

    def on_mouse_leave(self, x, y):
        self.state = 'base'
        self.draw()

    def on_mouse_drag_enter(self, x, y):
        pass

    def on_mouse_drag_leave(self, x, y):
        self.state = 'base'
        self.draw()


Button.register_event_type('on_click')

class Entry (Widget):
    pass



