#!/usr/bin/env python3

import pyglet
import glooey
import autoprop
import datetime
from pyglet.gl import *
from vecrec import Vector, Rect

@autoprop
class LineClock(glooey.Widget):
    custom_radius = 50
    custom_color = 'green'
    custom_hour_hand_width = 3
    custom_minute_hand_width = 2
    custom_second_hand_width = 1
    custom_face_border_width = 3

    def __init__(self):
        super().__init__()

        # User-controlled attributes:
        self._radius = self.custom_radius
        self._color = self.custom_color

        # Internal attributes:
        self._face = None
        self._hands = {
                'hour': glooey.drawing.Rectangle(),
                'min': glooey.drawing.Rectangle(),
                'sec': glooey.drawing.Rectangle(),
        }

    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        self._repack()

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color
        self._draw()

    def on_update(self, dt):
        self._draw()

    def do_attach(self):
        # Update the clock ten times a second.  
        pyglet.clock.schedule_interval(self.on_update, 1/10)

    def do_detach(self):
        pyglet.clock.unschedule(self.on_update)
    
    def do_claim(self):
        width = height = 2 * self.radius
        return width, height

    def do_regroup(self):
        if self._face is not None:
            self.batch.migrate(
                    self._face, GL_TRIANGLE_STRIP, self.group, self.batch)

        for k in self._hands:
            self._hands[k].batch = self.batch
            self._hands[k].group = HandGroup(self)

    def do_draw(self):
        self.do_draw_face()
        self.do_draw_hands()

    def do_draw_face(self):
        N = 48
        vertices = []

        for i in range(N + 2):
            direction = Vector.from_degrees(360 * i / N)
            radius = self._radius - (i % 2 * self.custom_face_border_width)
            vertex = self.rect.center + radius * direction
            vertices += vertex.tuple

        # Insert duplicate vertices at the beginning and end of the list, 
        # otherwise this triangle strip will end up connected to any other 
        # triangle strips in the scene.

        vertices = vertices[:2] + vertices + vertices[-2:]
        num_vertices = len(vertices) // 2

        color = glooey.drawing.Color.from_anything(self._color)
        colors = num_vertices * color.rgb

        # The vertex list for the face may or may not exist yet, e.g. if the 
        # clock is being drawn for the first time or was previously being 
        # hidden.  So create the vertex list if we need to, otherwise just 
        # update its coordinates.

        if self._face is None:
            self._face = self.batch.add(
                    num_vertices,
                    GL_TRIANGLE_STRIP,
                    self.group,
                    ('v2f', vertices),
                    ('c3B', colors),
            )
        else:
            self._face.vertices = vertices
            self._face.colors = colors

    def do_draw_hands(self):
        # We're hard-coding the radii of the hands here.  Probably it would be 
        # better to make separate attributes for these, but I think that would 
        # start to detract from the clarity of the example.

        rects = {
            'hour': Rect.from_size(self.custom_hour_hand_width, self.radius/2),
            'min': Rect.from_size(self.custom_minute_hand_width, self.radius),
            'sec': Rect.from_size(self.custom_second_hand_width, self.radius),
        }

        # The clock hands all start pointing towards 12:00, and the rotations 
        # are clockwise, so 90° is 3:00, 180° is 6:00, 270° is 9:00, etc.

        now = datetime.datetime.now()
        angles = {
            'hour': 360 * now.hour / 12,
            'min': 360 * now.minute / 60,
            'sec': 360 * now.second / 60,
        }

        for k in self._hands:
            rects[k].bottom = 0
            rects[k].center_x = 0

            self._hands[k].rect = rects[k]
            self._hands[k].group.angle = angles[k]
            self._hands[k].color = self._color
            self._hands[k].show()

    def do_undraw(self):
        if self._face is not None:
            self._face.delete()
            self._face = None

        for k in self._hands:
            self._hands[k].hide()


class HandGroup(pyglet.graphics.Group):

    def __init__(self, clock):
        super().__init__(parent=clock.group)
        self.clock = clock
        self.angle = 0

    def set_state(self):
        x, y = self.clock.rect.center
        clockwise = -1

        glPushMatrix()
        glLoadIdentity()
        glTranslatef(x, y, 0)
        glRotatef(self.angle, 0, 0, clockwise)

    def unset_state(self):
        glPopMatrix()



window = pyglet.window.Window()
gui = glooey.Gui(window)
gui.add(LineClock())
pyglet.app.run()


