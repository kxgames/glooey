***************
Troubleshooting
***************

Glooey includes a few tools to help you figure out what's going wrong when 
things don't work like you expect them to.  Perhaps the most difficult problem 
to diagnose is when a widget simply doesn't appear on the screen.  To help with 
this, widgets have a method called `~Widget.debug_drawing_problems()`.  This 
method checks the internal state of the widget and suggests reasons why it 
might not be showing up.  These reasons include things like:

- It (or one of it's parents) is not attached to the GUI. [#]_
- It was never assigned any space by its parent.
- It was assigned a 0x0 rectangle by its parent.
- It was never given a pyglet graphics group by it's parent.

For example, consider the following program.  Normally placeholders fill all 
the space that's available to them, but the top-left alignment specified here 
tells the placeholder to make itself as small as possible and to go into the 
top-left corner.  Placeholders are happy to make themselves 0x0 because they 
don't have any "real" content, and as a result the screen is black.

.. demo:: troubleshooting/debug_drawing_problems.py

   window = pyglet.window.Window()
   gui = glooey.Gui(window)

   widget = glooey.Placeholder()
   widget.alignment = 'top left'

   gui.add(widget)

If we add a call to `~Widget.debug_drawing_problems()` after the widget has 
been attached to the GUI, it'll pretty much tell us what's going on::
  
   gui.add(widget)
   widget.debug_drawing_problems()

::

   Placeholder(id=dda0) was given no space because it requested 0x0.
   Check for bugs in Placeholder.do_claim()

It can also be difficult to diagnose why widgets aren't appearing where you 
think they should be.  To help with this, widgets have a method called 
`~Widget.debug_placement_problems()`.  This method draws three rectangles 
relevant to how the widget is being placed:

- Red rectangle: What size the widget claimed.  This rectangle is always in the 
  lower left corner, because claims only have widths and heights --- not 
  positions.

- Yellow rectangle: The space the widget was assigned by its parent
  
- Blue rectangle: The space the widget ultimately took.
  
For example:

.. demo:: troubleshooting/debug_placement_problems.py

   window = pyglet.window.Window()
   gui = glooey.Gui(window)
   gui.padding = 50

   widget = glooey.Placeholder(200, 100)
   widget.alignment = 'top left'

   gui.add(widget)
   widget.debug_placement_problems()

Here we can see the 200x100 red rectangle in the bottom left corner, the yellow 
rectangle that's inset 50px from the edge of the screen due to the padding, and 
the blue rectangle that's the same size as the actual widget.  Also notice that 
the blue and yellow rectangles overlap, and that the yellow one is on top.  
It's not uncommon for the blue rectangle to be completely covered by the yellow 
one, so don't be alarmed if you can't see it.

If neither of these tools solve your problem, make an `issue`__ on Github and 
I'll try to help you out!

__ https://github.com/kxgames/glooey/issues

.. [#] If one of the parents is the problem, it'll even tell you which one!
