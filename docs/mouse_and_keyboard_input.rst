************************
Mouse and keyboard input
************************

Input handling in glooey is built on the pyglet event framework.  You can read 
all about this framework `here`__, but the basic idea is that events are 
triggered when input occurs, and your code can react to these events however it 
likes.  Glooey works the same way, but events are triggered by every widget 
that's affected by the input in question.  Another way to say this is that 
every widget is an `EventDispatcher`.  So while pyglet lets you react when the 
mouse is clicked, glooey lets you react when the mouse is clicked on a 
particular widget.

__ https://pyglet.readthedocs.io/en/latest/programming_guide/events.html

The following sections will describe the user-input-related events that widgets 
can trigger, but the first thing to know is how to react to an event.  You do 
this by attaching a handler (which is a function with the same name and 
signature as the event) to a widget.  There are two prominent ways to do this.  
The first is to use the `~Widget.event()` decorator::

   @widget.event
   def on_click(widget):
      print(f"{widget} was clicked!")

The second is to use the `~Widget.push_handlers()` method::

   def on_click(widget):
      print(f"{widget} was clicked!")
   widget.push_handlers(on_click)

Handlers that have been pushed can also be popped, which is sometimes useful::

   widget.pop_handlers()

Mouse input
===========
Every widget can dispatch the following events in response to mouse input:

``on_click(widget)``
   Triggered when the user clicks on a widget.  This is pretty similar to 
   ``on_mouse_release()``, but there are a few differences.  First, a widget 
   cannot be clicked if it's not "enabled", i.e. via `~Widget.enable()` and 
   `~Widget.disable()`.  (You can think of a disabled widget as being 
   "greyed-out", although it's up to the widget itself to actually change it's 
   appearance when it's been disabled.)  Second, a widget cannot be clicked if 
   the click didn't begin within the widget.  In other words, if you were to 
   drag the mouse over a widget and then release it, that would not be a click.

``on_double_click(widget)``
   Triggered when the user clicks the same widget twice within 500 ms.  The 
   second click triggers both ``on_click()`` and ``on_double_click()`` events.

``on_rollover(widget, current_state, previous_state)``
   Triggered whenever a widget's rollover state changes.  There are three 
   possible states: 'base' (the mouse is not interacting with the widget), 
   'over' (the mouse is currently hovering over the widget), and 'down' (the 
   mouse is in the middle of clicking on the widget).

``on_mouse_press(x, y, button, modifiers)``
   Triggered when the mouse is pressed while over a widget. 

``on_mouse_release(x, y, button, modifiers)``
   Triggered when the mouse is released while over a widget.

``on_mouse_hold(dt)``
   Triggered 60 times a second whenever the mouse is being pressed on a widget 
   (if the press began on the widget).  The ``dt`` argument gives the amount of 
   time that passed between triggers.
   
``on_mouse_motion(x, y, dx, dy)``
   Triggered when the mouse moves around inside a widget.

``on_mouse_enter(x, y)``
   Triggered when the mouse moves into a widget.  Note that pyglet only uses 
   this event to indicate when the mouse enters the window, so in this sense 
   glooey treats each widget like its own window.

``on_mouse_leave(x, y)``
   Triggered when the mouse moves out of a widget.  Note that pyglet only uses 
   this event to indicate when the mouse leaves the window, so in this sense 
   glooey treats each widget like its own window.

``on_mouse_drag(x, y, dx, dy, buttons, modifiers)``
   Triggered when the mouse is dragged around inside a widget.

``on_mouse_drag_enter(x, y)``
   Triggered when the mouse is dragged into a widget.  Note that pyglet only 
   uses this event to indicate when the mouse leaves the window, so in this 
   sense glooey treats each widget like its own window.

``on_mouse_drag_leave(x, y)``
   Triggered when the mouse is dragged out of a widget.  Note that pyglet only 
   uses this event to indicate when the mouse leaves the window, so in this 
   sense glooey treats each widget like its own window.

``on_mouse_scroll(x, y, scroll_x, scroll_y)``
   Triggered when the scroll wheel is turned while the mouse is over a widget.

In addition to the above events that can be triggered by any widget, the 
following events can be triggered only by certain widgets:

``on_toggle(widget)``
   Triggered by Checkbox and RadioButton when the state of the button is 
   changed.  This can happen programmatically, but usually happens because the 
   user clicked on it.

``on_mouse_pan(direction, dt)``
   Triggered by PanningGui when the mouse is at the edge of the screen.  The 
   Viewport widget can listen for these events and use them to pan around a 
   larger widget, so together these widgets are useful for making fullscreen 
   games.

Keyboard input
==============
This section should really be empty; glooey doesn't affect how keyboard events 
are handled at all.  If you want to react to keyboard input (e.g. to make a 
hotkey), just attach a ``on_key_press`` and/or ``on_key_release`` handlers to 
the window just like you would in any pyglet program.  Certain widgets (like 
`Form`) do interact with the keyboard, but they do so by directly interacting 
with the window themselves, and they don't re-dispatch keyboard related events.

