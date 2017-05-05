You should only have to reimplement methods that begin with ``do_`` or ``on_``.

When making a container widget, make sure you call both ``_attach_child()`` and 
``_resize_and_regroup_children()`` when attaching a new child widget.

How to write a new widget
=========================
You will need to write your own widget if you want functionality that is not 
provided by the basic widgets included with ``glooey``, like a mini-map in a 
strategy game for example.  Each widget is responsible for two things:

- Claiming the space it needs.
- Drawing itself.

Claiming space
--------------
The first responsibility of a widget is to claim the space it will need to draw 
itself.  Note that this is subtly different from how much space it will 
actually get.  The size claimed by the widget should be the minimum size needed 
to fit all the graphical elements associated with that widget.  When the widget 
is added to a container, its parent will decide how much space it will actually 
get, which will typically (but not necessarily) be equal to or larger than the 
claimed minimum size.  An exception is raised if the widgets can't fit on the 
screen.

To claim space for a widget, set ``self.min_width`` and ``self.min_height`` in 
its ``claim()`` method::

   class MyWidget:
       def claim(self):
           self.min_width = 50
           self.min_height = 10

Hopefully this simple example gets the point across, but it's worth noting that 
this method is often much more complicated in real widgets.  For Label widgets 
it has to calculate the amount of space the label text will take up, for Image 
widgets it has to use the size of the image, and for container widgets it has 
to consider the space claimed by all of its children.

Keep in mind that the ``claim()`` method may be called several times each time 
the layout has to be recalculated, so its best to avoid having it do anything 
too expensive.  If this becomes a serious limitation or performance issue, the 
results from claim could be cached, but at this point caching seems like more 
complexity and more potential for staleness bugs than it's worth.

Drawing
-------
The second responsibility of a widget is to draw itself.  Widgets have two 
methods related to this responsibility: ``draw()`` and ``undraw()``.  The 
former is called when the widget is first made visible and every time it might 
need to be redrawn (i.e. after resizing).  The latter is called when the widget 
is removed from the GUI.

Most of the drawing functions in ``pyglet`` take group and batch arguments.  
Each widget has ``group`` and ``batch`` attributes, both derived from the 
widget's parent.  The ``group`` attribute can be used to make sure your widget 
z-orders properly with the widgets around it, and the ``batch`` attribute can 
be used to make sure the GUI renders efficiently.
