***************************
Making widgets from scratch
***************************

Sometimes you need a widget that is totally unlike any of the built-in ones.  
This scenario comes up fairly often in game programming, which lends itself to 
non-standard user interfaces.  When this happens, you have no option but to 
write your own widget class from scratch.  The `how_it_all_works` tutorial 
describes all the things that a widget needs to do, but that information would 
be hard to apply in practice without some examples.  This tutorial has three 
examples: two showing how the make "normal" widgets and one showing how to make 
a container widget.  Each example goes into a lot of detail, but here are the 
important points to remember:

- Always implement `~Widget.do_claim()`.
- Remember that `~Widget.do_draw()` may be called multiple times, so check 
  whether the things you're drawing (sprites, vertex lists, etc.) need to be 
  created or just updated.
- Always call `~Widget._repack()` after doing something that might change the 
  size of the widget.
- Always call `~Widget._draw()` after doing something that might change the 
  appearance of the widget.
- Always call `~Widget._repack_and_regroup_children()` after adding or removing 
  a child widget (unless you do it in the constructor).

Making a custom widget
======================
You should make a custom widget when you want to achieve a graphical effect 
that the existing widgets just can't manage.  The example we'll be working with 
here is a clock.  This is a good example because there's no way to make 
rotating clock hands with the standard widgets.

We'll actually go over two different ways to implement a clock widget.  In the 
first example, we'll draw the clock using images and sprites.  This should be 
applicable to a lot of custom widgets, since most user-interface elements are 
built from images.  In the second example, we'll draw the clock using OpenGL 
primitives.  This won't be as pretty, but it'll show how a widget can harness 
the full power of OpenGL.

Using images and sprites
------------------------
.. demo:: making_widgets_from_scratch/image_clock.py

   class VintageClock(ImageClock):
       custom_face = pyglet.image.load('face.png')
       custom_face.anchor_x, custom_face.anchor_y = 150, 150
       custom_hour_hand = pyglet.image.load('hour_hand.png')
       custom_hour_hand.anchor_x, custom_hour_hand.anchor_y = 13, 0
       custom_minute_hand = pyglet.image.load('minute_hand.png')
       custom_minute_hand.anchor_x, custom_minute_hand.anchor_y = 9, 0
       custom_second_hand = pyglet.image.load('second_hand.png')
       custom_second_hand.anchor_x, custom_second_hand.anchor_y = 4, 24

   window = pyglet.window.Window()
   gui = glooey.Gui(window)
   gui.add(VintageClock())

Let's begin by looking at the definition of the custom widget class and its 
attributes::

   @autoprop
   class ImageClock(glooey.Widget):
       custom_face = None
       custom_hour_hand = None
       custom_minute_hand = None
       custom_second_hand = None

       def __init__(self):
           super().__init__()
           self._images = {
                   'face': self.custom_face,
                   'hour': self.custom_hour_hand,
                   'min': self.custom_minute_hand,
                   'sec': self.custom_second_hand,
           }
           self._sprites = {
                   'face': None,
                   'hour': None,
                   'min': None,
                   'sec': None,
           }

The "custom" attributes will allow subclasses to provide particular images for 
the various parts of the clock.  Internally, the widget maintains dictionaries 
of both these images and sprite objects that will be used to render them.

.. code::
    
       def get_face(self):
           return self._images['face']

       def set_face(self, image):
           self._images['face'] = image
           self._repack()

The complete widget has similar getters and setters for all of the images, but 
we only need to look at one here because they're all the same.  The important 
part is the call to `self._repack() <Widget._repack>`.  This should be done 
whenever the widget's size may have changed, because it causes glooey to 
recalculate how much space each widget should have.  In this case, if the clock 
is given a new face, its size may very well change.

Another thing to draw attention to is the ``@autoprop`` class decorator that I 
glossed over in the first snippet.  This decorator automatically creates 
properties (e.g. ``self.face``) for each group of getters and setters.  This is 
nice because it makes attribute access clear and concise for users of our 
widget, without requiring hardly any boilerplate from us.  You don't need to 
use this decorator in your own widgets, but all of the built-in widgets use it, 
so I thought it'd be good to mention.  For more information, check out the 
`autoprop on Github`__.

__ https://github.com/kalekundert/autoprop

.. code::

       def do_claim(self):
           width, height = 0, 0
           min_size = 0

           if 'face' in self._images:
               width = self._images['face'].width
               height = self._images['face'].height

           # Since the hands can rotate, we need to claim enough space to fit the 
           # largest hand in both dimensions.

           for k in ['hour', 'min', 'sec']:
               if k in self._images:
                   min_size = max(min_size, self._images[k].width)
                   min_size = max(min_size, self._images[k].height)

           return max(width, min_size), max(height, min_size)

The `~Widget.do_claim()` method returns the minimum amount if space needed by 
the widget, and must be implemented by every new widget (i.e. it's pure 
virtual).  This particular implementation is a bit convoluted because we need 
to account for the fact that none of the images are required (e.g. the user 
might not specify a clock face) and that the hands will be rotating, but 
hopefully the concept is straight-forward.

.. code::

       def do_regroup(self):
           for sprite in self._sprites.values():
               if sprite is not None:
                   sprite.batch = self.batch
                   sprite.group = self._get_layer(k)

       def _get_layer(self, key):
           layers = {
                   'face': 0,
                   'hour': 1,
                   'min': 2,
                   'sec': 3,
           }
           return pyglet.graphics.OrderedGroup(layers[key], self.group)

The `~Widget.do_regroup()` method is called when the widget is assigned to a 
new group.  This always happens when the widget is attached to the GUI, and may 
also happen if the widget is moved from one parent to another within the GUI.  
The above code actually won't do anything in the first case, because the 
sprites are all ``None`` until the widget is drawn for the first time, but in 
the second case it will properly update the sprites.

Note that the sprites need to be in separate groups to ensure that they are 
drawn in the correct order.  The logic for doing this was factored out into the 
``_get_layer()`` method, because it'll also be used in `~Widget.do_draw()`.

.. code::

       def do_draw(self):
           now = datetime.datetime.now()
           rotations = {
                   'hour': 360 * now.hour / 12,
                   'min': 360 * now.minute / 60,
                   'sec': 360 * now.second / 60,
           }
           for k in self._sprites:
               if self._images[k] is None:
                   if self._sprites[k] is not None:
                       self._sprite.delete()
                       self._sprites[k] = None
                   continue

               if self._sprites[k] is None:
                   self._sprites[k] = pyglet.sprite.Sprite(
                           self._images[k],
                           batch=self.batch,
                           group=self._get_layer(k),
                   )
               else:
                   self._sprites[k].image = self._images[k]

               # The following lines assume that each image has `anchor_x` and 
               # `anchor_y` properties indicating where the center of the clock 
               # should be.

               self._sprites[k].x = self.rect.center_x
               self._sprites[k].y = self.rect.center_y
               if k in rotations:
                   self._sprites[k].rotation = rotations[k]

       def do_undraw(self):
           for k in self._sprites:
               if self._sprites[k] is not None:
                   self._sprites[k].delete()
                   self._sprites[k] = None
                
The `~Widget.do_draw()` method is called whenever the widget's appearance may 
have changed.  A perennial complexity with this method is that you have to 
check if the vertex lists that make up the widget already exist or not.  They 
won't if the widget is being drawn for the first time (or was previously 
undrawn), otherwise they will.  This is the motivation behind the various 
``None`` checks littering this method.  Also note that the rotation of each 
clock hand is based on the current time.

The `~Widget.do_undraw()` method just deletes all the vertex lists associated 
with the widget.  It also resets the sprites to ``None``, so that 
`~Widget.do_draw()` knows to recreate them the next time it's called. 

.. code::

       def on_update(self, dt):
           self._draw()

       def do_attach(self):
           pyglet.clock.schedule_interval(self.on_update, 1)

       def do_detach(self):
           pyglet.clock.unschedule(self.on_update)

Most widgets don't need to react to being attached or detached from the GUI, 
but this is a good example of a widget that does!  To keep the clock 
up-to-date, we need to redraw it every second.  These methods setup and 
teardown a handler to do that for as long as the widget is attached to the GUI.
    
Using OpenGL primitives
-----------------------
.. demo:: making_widgets_from_scratch/line_clock.py

   window = pyglet.window.Window()
   gui = glooey.Gui(window)
   gui.add(LineClock())

As before, lets begin by looking at the definition of the custom widget class 
and its attributes::

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

Now that we'll be drawing the clock and its hands ourselves, we have attributes 
that define its geometry.  Our strategy for drawing the hands will be to draw 
rectangles located at the origin and to position them on the clock face using  
``glTranslate()`` and ``glRotate()``.  Note that we're using 
`glooey.drawing.artists.Rectangle` to draw the rectangles.  The 
`glooey.drawing` module comes with a few different "artists" like this to help 
draw simple shapes.  We'll be on our own for the clock face, but that actually 
makes this class an even better demonstration because it'll show both how to 
use raw OpenGL primitives (for the face) and how much simpler things can be if 
you don't have to do that (for the hands).

.. code::

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

The thing to notice in these methods is that ``set_radius()`` calls 
`~Widget._repack()` while ``set_color()`` calls `~Widget._draw()`.  This is 
because ``set_radius()`` can change the size of widget, while ``set_color()`` 
can only change its appearance.  Also note that you never need to call 
`~Widget._repack()` and `~Widget._draw()` in the same method; widgets are 
automatically redrawn when they're repacked.

.. code::

       def do_claim(self):
           width = height = 2 * self.radius
           return width, height

Calculating the minimum width and height needed by this widget is trivial, 
because we have a radius.

.. code::

       def do_regroup(self):
           if self._face is not None:
               self.batch.migrate(
                       self._face, GL_TRIANGLE_STRIP, self.group, self.batch)

           for k in self._hands:
               self._hands[k].batch = self.batch
               self._hands[k].group = HandGroup(self)

Regrouping is particularly important for this clock implementation, because 
groups are how we'll rotate and translate the hands.  Specifically, we'll put 
the rectangle artists representing the hands in custom ``HandGroup`` groups 
which will apply the proper transformations --- see the definition of the 
``HandGroup`` class below.  Note also that the face (vertex list) and the hands 
(artists) are updated differently.  For the face, we call 
:meth:`pyglet.graphics.Batch.migrate` if the vertex list has already been 
drawn.  For the hands, we just need to set the batch and group attributes, 
regardless of whether or not they've been drawn before.  The rectangle artist 
will take care of migrating the vertex lists if they exist.

.. code::

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

Groups are the mechanism by which you can set and unset OpenGL state while 
rendering with pyglet.  For a complete introduction, see the `relevant pyglet 
documentation`__.  For our purposes here, it is enough to know that groups have 
a :meth:`~pyglet.graphics.Group.set_state` method to configure the OpenGL state 
and an :meth:`~pyglet.graphics.Group.unset_state()` method to restore it.  A 
group can also have a parent, in which case the parent's state will be applied 
just before the child's.

__ https://pyglet.readthedocs.io/en/pyglet-1.2-maintenance/api/pyglet/pyglet.graphics.html

In the constructor, we initialize the ``HandGroup`` with the clock's group as its 
parent.  This way, if the clock has a group that (for example) puts it above or 
below other widgets, the hands will respect that ordering.  The 
:meth:`~pyglet.graphics.Group.set_state()` method takes care of the necessary 
translation and rotation.  It's important that the translation be done first, 
because we want to translate in the original coordinate frame, not the rotated 
one.  ``glPushMatrix()`` and ``glPopMatrix()`` are used to easily restore the 
OpenGL state once the hands are finished rendering.

.. code::

   # class LineClock (cont.)

       def do_draw(self):
           self.do_draw_face()
           self.do_draw_hands()

For clarity, the drawing routine has been broken into two separate methods:

.. code::

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

The clock face is drawn using the basic OpenGL primitives.  More specifically, 
the face is a triangle strip with vertices alternating between an inner and 
outer radius, creating a circular outline of a certain width.  We have to 
duplicate the first and last vertices in order to keep the triangle strip 
separate from any other triangle strips we might use.  The only part specific 
to glooey is at the end, where we decide whether to create a new vertex list or 
to update an existing one.

.. code::

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

In contrast, the clock hands are drawn using rectangle artists.  We begin by 
creating rectangles of the proper shape, with one end centered on the origin 
(which will become the center of the clock after the translation) and the other 
end pointing towards 12 o'clock (which will become the current time after the 
rotation).  We then calculate how much to rotate each hand based on the current 
time.  Lastly, we update the artists with the new rectangles and their groups 
with the new angles.  The artists will take care of creating or updating their 
vertex lists as necessary.

.. code::

       def do_undraw(self):
           if self._face is not None:
               self._face.delete()
               self._face = None

           for k in self._hands:
               self._hands[k].hide()

Since the clock face is a simple vertex list, we need to check that it exists 
before trying to delete it.  The clock hands we can just tell to hide, and the 
artists will take care of the details.

Making a custom container
=========================
Another reason you might need to write a custom widget is to control the 
placement of other GUI elements.  Such widgets are called containers, although 
there's nothing really to distinguish them from normal widgets other than how 
they behave (i.e. they don't inherit from a different class, and they could 
draw things if they wanted to).  The built-in containers are pretty flexible, 
so you should double-check to make sure none of them do what you want before 
trying to write your own.  `Grid`, `HBox`, and `VBox` are very good for 
traditional layouts, and `Board` is very good for more ad hoc layouts.

The example here will be a custom container that positions its children in a 
circle.  More specifically, the container will be given a radius and will 
position the center of each child at that radius.  It will also keep its 
children evenly spaced, so as children or added or removed, it will adjust the 
angle at which each is positioned.  It would be possible to obtain a similar 
layout using the `Board` container, but it would be very cumbersome, so we are 
justified in writing this "Ring" container from scratch.

Here is how our container will look in action.  We start by creating a ring 
instance and adding ten green placeholders to it, then we demonstrate that we 
can subsequently add or remove widgets by replacing every other green 
placeholder with an orange one:

.. demo:: making_widgets_from_scratch/ring.py

   window = pyglet.window.Window()
   gui = glooey.Gui(window)
   ring = Ring(radius=150)

   for i in range(10):
       green = glooey.Placeholder(50, 50)
       ring.add(green)

   for i in range(0, 10, 2):
       orange = glooey.Placeholder(50, 50, 'orange')
       ring.replace(ring.children[i], orange)

   gui.add(ring)

Let's begin by looking at the definition of the custom container class and its 
attributes::

   @autoprop
   class Ring(glooey.Widget):
       custom_radius = 150

       def __init__(self, radius=None):
           super().__init__()
           self._children = []
           self._radius = radius or self.custom_radius

       def get_children(self):
           # Return a copy of the list so the caller can't mess up our internal 
           # state by adding or removing things.
           return self._children[:]

       def get_radius(self):
           return self._radius

       def set_radius(self, radius):
           self._radius = radius
           self._repack()

We have two attributes: the radius and this list of children.  The radius can 
be set at the class-level (using ``custom_radius``) or at the instance-level 
(using the constructor or ``set_radius()``).  Note that ``set_radius()`` calls 
`~Widget._repack()`, since changing the radius will certainly change to amount 
of space needed by the widget and all its children.  The list of children can 
be modified using the ``add()``, ``remove()``, etc. methods (see below), but we 
also provide a read-only getter.

.. code::

       def add(self, widget):
           self.insert(widget, len(self._children))

       def insert(self, widget, index):
           self._attach_child(widget)
           self._children.insert(index, widget)
           self._repack_and_regroup_children()

       def replace(self, old_widget, new_widget):
           i = self._children.index(old_widget)
           with self.hold_updates():
               self.remove(old_widget)
               self.insert(new_widget, i)

       def remove(self, widget):
           self._detach_child(widget)
           self._children.remove(widget)
           self._repack_and_regroup_children()

       def clear(self):
           with self.hold_updates():
               for child in self._children[:]:
                   self.remove(child)

Let's begin by looking at the ``insert()`` method.  The three steps taken by this 
method are very characteristic of how a widget should be added to a container:

1. ``self._attach_child(widget)``: The first step is to attach the widget and 
   all of its children to the hierarchy so that they are considered when the 
   GUI is being rendered, when mouse events are being propagated, etc.  This 
   does not assign space to the new widget, so if we were to stop here, the new 
   widget would not be rendered until the next time the container was repacked.
   
2. ``self._children.insert(index, widget)``: The second step is to update the 
   internal data structures the container will use to figure out where each 
   child should go.  This should be done after `~Widget._attach_child()`; there 
   are several reasons why trying to attach a widget might raise an exception, 
   and you don't want your widget to end up in a corrupt state if that happens.

3. ``self._repack_and_regroup_children()``: The third and final step is to 
   update all of the container's children.  That means repacking the container 
   itself to make space for the new widget, and recalculating groups for each 
   of its children.  The rule of thumb is that any time 
   `~Widget._attach_child()` or `~Widget._detach_child()` is called outside the 
   constructor, `~Widget._repack_and_regroup_children()` should be called 
   afterwards.

The ``remove()`` method is the same idea, but in reverse, and the remaining 
methods just build on those two.  The one interesting thing about some of those 
remaining methods is that they use the `~Widget.hold_updates()` context manager 
to avoid triggering multiple repacks.  The context manager basically catches 
any calls to potentially expensive update methods (specifically: 
`~Widget._repack()`, `~Widget._draw()`, and 
`~Widget._repack_and_regroup_children()`) and defers them to the end of the 
with-block.  If the same method is called multiple times, it is only called 
once when the block ends.  This can be a useful way to reuse methods like 
``insert()`` and ``remove()`` without repacking the GUI more than once.

.. code::

       def do_claim(self):
           top = bottom = left = right = 0

           for child, offset in self._yield_offsets():
               top = max(top, offset.y + child.claimed_height / 2)
               bottom = min(bottom, offset.y - child.claimed_height / 2)
               left = min(left, offset.x - child.claimed_width / 2)
               right = max(right, offset.x + child.claimed_width / 2)

           return right - left, top - bottom

       def _yield_offsets(self):
           N = len(self._children)
           for i, child in enumerate(self._children):
               offset = self.radius * Vector.from_degrees(360 * i / N)
               yield child, offset

The `~Widget.do_claim()` method returns the minimum width and height needed to 
fit all the children.  It does this by basically mock-placing each child and 
calculating the greatest offsets in the horizontal and vertical directions.  
The `~Widget.do_resize_children()` method ends up pretty similar, since it's 
actually placing the children, so the ``_yield_offsets()`` helper factors out 
some shared code.

.. code::

       def do_resize_children(self):
           for child, offset in self._yield_offsets():
               rect = child.claimed_rect.copy()
               rect.center = self.rect.center + offset
               child._resize(rect)

This method is how containers position their children.  It's job is to call 
`~Widget._resize()` to provide a new rectangle to each of its children.  That 
rectangle should be at least as large as that child's claim, which is 
accessible via the `~Widget.claimed_rect` property.  This implementation gives 
each child exactly the space it claimed, but positions it along the edge of a 
circle centered at the center of the container itself.
