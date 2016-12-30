****************************************************
glooey --- An object-oriented GUI library for pyglet
****************************************************

Widget Wishlist
===============
Containers:
[X] Gui
[ ] Dialog
[X] PanningGui
[X] Viewport
[X] Frame
[X] Grid
[X] Stack
[X] HBoX
[X] VBoX
[ ] HScrollBoX
[ ] VScrollBoX
[ ] HVScrollBoX

Widgets:
[X] Label
[ ] Entry
[X] Image
[ ] Background
[X] Button
[X] CheckboX
[X] RadioButton
[ ] DropdownMenu
[ ] ToolTip

Bugs
====
- Attaching on_mouse_press handlers that add or remove widgets to those same 
  widgets is broken in some confusing way...

Implementation thoughts
=======================
- Implementing Entry will require me to implement keyboard grabbing.  I don't 
  think this will be too hard.  Every keyboard event will pass through the root 
  widget.  If anything has grabbed keyboard focus from it, the events will pass 
  to it.  Otherwise, the root will handle any global hotkeys that have been 
  configured.

- Implementing DropdownMenu and ScrollBox will require some semi-fancy OpenGL, 
  but both widgets should ultimately be very similar to Viewport.  In fact, I 
  think Viewport should inherit from ScrollBox.  (ScrollBox would just have the 
  scrolling function.  There would have to be another widget to act as the 
  scroll bar.)  Also, ScrollBox/Viewport should use glScissor() instead of the 
  stencil test.

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

  Background also blurs the line between artists and widgets.  I don't really 
  want Background to be a widget because widgets are fairly heavy-weight.  More 
  precisely, increasing the depth on the widget hierarchy increases the number 
  of functions that need to be called to handle mouse motion events.  For such 
  a static entity like Background, incurring this cost seems wasteful.  At the 
  same time, Background behaves like a widget in the sense that it's role is 
  basically to position a number of tiled image artists in a grid.  

  I think this blurring is maybe a symptom of widgets violating the single- 
  responsibility principle.  For example, the grid is responsible for both 
  managing child widgets and positioning rectangles in a grid.  I think I 
  haven't really counted the former responsibility before because it's fairly 
  trivial and basically the same for every container widget.  But it's not 
  nothing.  I think I can make the whole library more flexible by creating 
  functions for each container (e.g. make_grid()) that take responsibility for 
  positioning rectangles.  The containers would just keep track of their 
  children and would use the aforementioned functions to position them.

  This separation of responsibilities would allow Background to use make_grid() 
  to layout TileableImage artists.  This approach has benefits and drawbacks.  
  The benefits are that it keeps the widget hierarchy as small as possible and 
  that TileableImage doesn't need to be a widget, which is good because the 
  Background widget will ultimately be able to do all the same things and more.  
  The drawback is that there's no mechanism for the artists to request more or 
  less space.  This is what using widgets buys you: flexibility in what can be 
  attached.  But being relatively static, Background doesn't need that.

  In general, I like the idea that widgets should be either fairly simple 
  wrappers around artists or layout functions, or more complex compositions of 
  other widgets.  Image and Label already fit this mold, because pyglet 
  basically comes with image and text "artists".  I just need to extend the 
  idea to Background and the container widgets.
