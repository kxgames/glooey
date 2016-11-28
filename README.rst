****************************************************
glooey --- An object-oriented GUI library for pyglet
****************************************************

Widget Wishlist
===============
Containers:
[x] Gui
[ ] Dialog
[x] PanningGui
[x] Viewport
[x] Frame
[x] Grid
[x] Stack
[x] HBox
[x] VBox
[ ] HScrollBox
[ ] VScrollBox
[ ] HVScrollBox

Widgets:
[x] Label
[ ] Entry
[x] Image
[ ] Background
[x] Button
[x] Checkbox
[x] RadioButton
[ ] DropdownMenu
[ ] ToolTip

Implementation thoughts
=======================
- Implementing Entry will require me to implement keyboard grabbing.  I don't 
  think this will be too hard.  Every keyboard event will pass through the root 
  widget.  If anything has grabbed keyboard focus from it, the events will pass 
  to it.  Otherwise, the root will handle any global hotkeys that have been 
  configured.

- Implementing DropdownMenu and ScrollBox will require some semi-fancy OpenGL, 
  but both widgets should ultimately be very similar to Viewport.

- Dialog and tooltip are similar in that they both won't have parents in the 
  traditional sense.  Dialog boxes will probably take a root widget and grab 
  all the mouse and keyboard focus from its window, but the root window won't 
  know anything about it.  Tooltips are more complicated.  They'll take a 
  regular widget.  When that widget is attached, the tooltip will have to 
  notice and attach itself.  It'll really be like a child that the parent 
  doesn't know about.  I haven't thought about this too much, but I think the 
  only way for this to work will be for do_attach() and do_resize() to become 
  events, so external objects like Tooltip can observe them.
  
  I'm not sure what to do about groups, though.  The tooltip will definitely 
  want to be above its parent.  Maybe the best way is to give the root widget 
  one or more OrderedGroups that are on top of everything else.  The Dialogs 
  and the Tooltips could use those to make sure they end up above everything 
  else.

- The challenge with Background will be implementing a sophisticated Artist 
  that can show edges and corners as necessary, and can tile vertically or 
  horizontally.
