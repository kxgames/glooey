Should widget setters automatically call repack(), regroup(), redraw(), or 
anything else like that to immediately update the GUI?

Arguments against
=================
- Users won't manually update widgets that often, so to the extent that 
  managing the automated updates is difficult or complicated, maybe it's not 
  worth it.

  The most common thing will be to setup the GUI once in the beginning and to 
  just let it go after that.  Things will update, but not really because the 
  user called a setter:

  button rollovers:
    Button can manually draw it background, and might even be able to eliminate 
    some unnecessary repacks by doing so.

  dialog boxes and tooltips appearing:
    ...

  status bars changing:
    This is the exception, because it's basically triggered by the user calling 
    set_status().  Still, this is a pretty specific case, and I could provide 
    an update() method that sets the status and repacks for convenience.

- Automatic updates add to the cognitive burden of subclassing widgets, and I 
  want to make subclassing widgets as easy as possible.

  Automatically updating setters will often cause the whole GUI to be repacked, 
  so they're expensive operations.  This is something you have to keep in mind 
  when implementing subclasses.  This also leads to it being more efficient to 
  configure widgets before adding them to the GUI, which makes sense if you 
  think about it, but isn't really intuitive.

- Automatic updates will never be as efficient as manual updates, because they 
  can't be lazy.  (Well, maybe they could, but that would make the system more 
  complex.  For example, I could basically have hold_updates() always on in the 
  background, then call apply_updates() on a heart beat or something.)

Arguments in favor
==================
- If setters don't automatically update, then users need to:

  - Remember to update widgets manually.
  - Know which update method is appropriate for the setters that were called 
    (repack, regroup, redraw, _do_resize_children)

  This could be alleviated with something very much like the HoldUpdates 
  framework, e.g. if updates were basically always held and there was an 
  update() function that applied all the held updates and cleared the update 
  queue.  Each setter would then call its appropriate updater as it does now, 
  but the actual update would be deferred until the user explicitly triggered 
  it.

- Automatic updates are more consistent.

  I do want widgets to automatically update sometimes, like when the mouse 
  rolls over a button.  If some updates are automatic and others aren't, users 
  have to be able to intuit which are which.  If all updates are automatic, 
  that's easy.

  Also, not every update can be deferred.  For example, Gui.set_cursor() pretty 
  much has to happen right away, because it just defers to a pyglet function.  
  The only way to defer this would be to keep a cursor attribute in GUI, which 
  seems wasteful since pyglet.Window already does that.

- Subclasses only need to worry about this when calling multiple setters at 
  once.  But I can reduce the need for this by providing more "atomic" setters.


Other considerations
====================
I could use a prefix other than ``set_`` for setters that could be expensive.  
I was thinking about this because setters are usually cheap, and I think it's 
bothering me that in glooey they can sometimes (depending on the circumstance) 
be very expensive.  Below are some alternatives I've thought of:

  ``update_``
  ``new_``

Also, in glooey the getters corresponding to the setters are of questionable 
value.

# vim: ts=2 sts=2 sw=2
