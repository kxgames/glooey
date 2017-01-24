Introduction
============
Right now button is a monolithic and fairly large class.  Granted, getters and 
setters make up a lot of its bulk, but its still not very powerful when it 
comes to implementing custom buttons.  It's easy enough to override the 
behaviors Button itself provides, like background rollovers and text and icons, 
but anything else requires basically writing your class from scratch.

Checkbox demonstrates this problem.  It's does almost the same thing as Button, 
but its a totally unrelated class.  In fact, a lot of code was copy-and-pasted 
between the two classes.

Conclusion
==========
I'll make the following classes:

- Clickable: emits on_click(), on_double_click(), and on_rollover() events.
- Rollover: Stateful subclass, observes a clickable and changes state in 
  response to on_rollover() events.
- Stateful: basic widget that just displays a single widget depending on its 
  current state. - 

Discussion
==========
Rollover will take it's cues from self, so I don't have to worry about the 
background and the button being out of sync.

How to handle non-square buttons?  I should think about this a bit just to make 
sure it's not too hard.

Maybe everything should be rollover-able and clickable.  Imagine wanting to 
select rows in a table.  Then, if every widget dispatches on_rollover events in 
response to on_mouse_... events, it would be easy enough to reconfigure when 
on_rollover events are triggered.  

Want to have some sort of _is_pixel_over_widget() method that the rollover 
target can reimplement to determine what the rollover state should be.  I 
definitely want this to be overloadable, because I can imagine implmenting it 
in a few different ways, e.g. you could load an image and look for black or 
white pixels, or for circular buttons you could just calculate a distance from 
the center.

And actually, don't need to have on_rollover() event.  Parent class decides 
when to call on_mouse_enter() and friends, so I just need to change the parent 
class logic (which is in Widget) to consider _is_pixel_over_widget().

But Button does need a way to know when it's been clicked.  on_mouse_release() 
isn't enough, because it triggers even if the mouse was dragged over the 
widget.  Rollover would know, but a button won't necessarily have one.  I could 
add the event to Widget.  That may be good anyways because I imagine it'll be 
pretty common to want to make custom widgets that are clickable (and that don't 
necessarily inherit from Button).  But then should every widget have rollover 
events?  Once I'm tracking clicks, I'm basically tracking rollovers anyway.  
Meh, it's not so bad to support clicks without supporting rollovers.

Also, if I give the Button a way to become inactive, any rollovers attached to 
it won't know about that.  That suggests that the lead object really needs to 
dispatch an event saying what it wants to happen, e.g. on_rollover(state) where 
state can be anything.  And I'm still a little antsy about putting a lot of 
clicking logic in Widget.  

So maybe I should make that Clickable class.  It would generate on_click() and 
on_rollover() events.  Rollover widgets could observe it.  I was trying to 
avoid inheritance, because I can see it making it difficult to compose things 
down the road, but I guess I won't feel so bad about merging Clickable into 
Widget if that happens.  I would make it a mixin class, but it needs to derive 
from EventDispatcher to register events, and I don't want diamond inheritance.

Actually, I could use __init_subclass__() to register events.  Maybe that's 
what I should do...

