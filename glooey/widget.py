import pyglet
import autoprop

from vecrec import Rect
from glooey import drawing
from glooey.helpers import *

class EventDispatcher(pyglet.event.EventDispatcher):

    def __init__(self):
        super().__init__()
        self.__timers = {}

    def start_event(self, event_type, *args, dt=1/60):
        # Don't bother scheduling a timer if nobody's listening.  This isn't 
        # great from a general-purpose perspective, because a long-lived event 
        # could have listeners attach and detach in the middle.  But I don't 
        # like the idea of making a bunch of clocks to spit out a bunch of 
        # events that are never used.  If I want to make this more general 
        # purpose, I could start and stop timers as necessary in the methods 
        # that add or remove handlers.
        if not any(self.__yield_handlers(event_type)):
            return

        def on_time_interval(dt):
            self.dispatch_event(event_type, *args, dt)

        pyglet.clock.schedule_interval(on_time_interval, dt)
        self.__timers[event_type] = on_time_interval

    def stop_event(self, event_type):
        if event_type in self.__timers:
            pyglet.clock.unschedule(self.__timers[event_type])

    def __yield_handlers(self, event_type):
        if event_type not in self.event_types:
            raise ValueError("%r not found in %r.event_types == %r" % (event_type, self, self.event_types))

        # Search handler stack for matching event handlers
        for frame in list(self._event_stack):
            if event_type in frame:
                yield frame[event_type]

        # Check instance for an event handler
        if hasattr(self, event_type):
            yield getattr(self, event_type)


@autoprop
class Widget(EventDispatcher, HoldUpdatesMixin):
    custom_size_hint = 0, 0
    custom_width_hint = None
    custom_height_hint = None

    custom_padding = None
    custom_horz_padding = None
    custom_vert_padding = None
    custom_left_padding = None
    custom_right_padding = None
    custom_top_padding = None
    custom_bottom_padding = None

    custom_alignment = 'fill'

    def __init__(self):
        EventDispatcher.__init__(self)
        HoldUpdatesMixin.__init__(self)

        self._root = None
        self._parent = None
        self._group = None

        # Use a double-underscore to avoid name conflicts; `_children` is a 
        # useful name for subclasses, so I don't want it to cause conflicts.
        self.__children = set()

        self._children_under_mouse = set()
        self._children_can_overlap = True
        self._mouse_grabber = None

        # The amount of space requested by the user for this widget.
        self._width_hint = first_not_none((
                self.custom_width_hint,
                self.custom_size_hint[0],
        ))
        self._height_hint = first_not_none((
                self.custom_height_hint,
                self.custom_size_hint[1],
        ))
        # The minimal amount of space needed to display the content of this 
        # widget.  This is a combination of the size returned by the widget's 
        # do_claim() method and any size hints manually set by the user.
        self._min_height = 0
        self._min_width = 0

        # The minimum amount of space containers need to allocate for this 
        # widget.  This is just the size of the content plus any padding.
        self._claimed_width = 0
        self._claimed_height = 0

        # The space assigned to the widget by it's parent.  This cannot be 
        # smaller than self.claimed_rect, but it can be larger.
        self._assigned_rect = None

        # The rect the widget show actually use to render itself.  This is 
        # determined by the alignment function from the content rect and the 
        # assigned rect.
        self._rect = None

        # The rect the widget will actually show, plus any padding.  This is 
        # basically the claimed rect, but with meaningful coordinates.
        self._padded_rect = None

        self._is_hidden = False
        self._is_parent_hidden = False
        self._is_claim_stale = True

        # Take care to avoid calling any potentially polymorphic methods, such 
        # as set_padding() or repack().  When these methods are overridden, 
        # they often become dependent on the overriding subclass being properly
        # initialized.  Since that hasn't happened by the time this constructor 
        # is called, these polymorphic methods can cause headaches.
        self._set_padding(
                all=self.custom_padding,
                horz=self.custom_horz_padding,
                vert=self.custom_vert_padding,
                left=self.custom_left_padding,
                right=self.custom_right_padding,
                top=self.custom_top_padding,
                bottom=self.custom_bottom_padding,
        )
        self._alignment = self.custom_alignment

    def __repr__(self):
        return '{}(id={})'.format(
                self.__class__.__name__,
                hex(id(self))[-4:],
        )

    def __iter__(self):
        yield from self.__children

    def __bool__(self):
        """
        Always consider widgets to be "true".

        This behavior is meant to facilitate comparisons against None.  This 
        method has to be explicitly implemented because otherwise python would 
        fallback on __len__(), which confusingly depends on whether or not the 
        widget has children.
        """
        return True

    def __len__(self):
        return len(self.__children)

    def __contains__(self, child):
        return child in self.__children

    @update_function
    def repack(self):
        if not self.is_attached_to_gui:
            return

        has_claim_changed = self.claim()

        # If the widget is a different size than it used to be, give its parent 
        # a chance to repack it.
        if has_claim_changed:
            self._is_claim_stale = False
            self.parent.repack()
            self._is_claim_stale = True

        # Otherwise, stop recursing and resize the widget's children.
        else:
            self.realign()

    def claim(self):
        # Only calculate the claim once during each repack.
        if not self._is_claim_stale:
            return False

        # Have each child widget claim space for itself, so this widget can 
        # take those space requirements into account.
        for child in self.__children:
            child.claim()

        # Make note of the previous claim, so we can say whether or not it has 
        # changed.
        previous_claim = self._claimed_width, self._claimed_height

        # Keep track of the amount of space the widget needs for itself (min_*) 
        # and for itself in addition to its padding (claimed_*).
        min_width, min_height = self.do_claim()

        self._min_width = max(min_width, self._width_hint)
        self._min_height = max(min_height, self._height_hint)

        horz_padding = self._left_padding + self._right_padding
        vert_padding = self._top_padding + self._bottom_padding

        self._claimed_width = self._min_width + horz_padding
        self._claimed_height = self._min_height + vert_padding

        # Return whether or not the claim has changed since the last repack.  
        # This determines whether the widget's parent needs to be repacked.
        return previous_claim != (self._claimed_width, self._claimed_height)

    def resize(self, new_rect):
        """
        Change the size or shape of this widget.

        This method is triggered by repack(), which recursively climbs the 
        widget hierarchy to make space for the widgets that need it, then calls 
        resize() on any widget that need to adapt to the new space allocation.

        This method should not be called outside of a repack, because it 
        assumes that the claims have already been updated.
        """
        self._assigned_rect = new_rect
        self.realign()

    def realign(self):
        # This method should not be called outside of a repack, because it 
        # assumes that the claims have already been updated.

        # Subtract padding from the full amount of space assigned to this 
        # widget.
        padded_rect = self._assigned_rect.copy()
        padded_rect.left += self.left_padding
        padded_rect.bottom += self.bottom_padding
        padded_rect.width -= self.total_horz_padding
        padded_rect.height -= self.total_vert_padding

        # Align this widget within the space available to it (i.e. the assigned 
        # space minus the padding).
        content_rect = Rect.from_size(self._min_width, self._min_height)
        drawing.align(self._alignment, content_rect, padded_rect)

        # Round the rectangle to the nearest integer pixel, because sometimes 
        # images can't line up right (e.g. in Background widgets) if the widget 
        # has fractional coordinates.
        content_rect.round()

        # Guarantee that do_resize() is only called if the size of the widget 
        # actually changed.  This is probably doesn't have a significant effect 
        # on performance, but hopefully it gives people reimplementing 
        # do_resize() less to worry about.
        if self._rect is None or self._rect != content_rect:
            self._rect = content_rect
            self._padded_rect = content_rect.copy()
            self._padded_rect.left -= self.left_padding
            self._padded_rect.bottom -= self.bottom_padding
            self._padded_rect.width += self.total_horz_padding
            self._padded_rect.height += self.total_vert_padding
            self.do_resize()

        # The children may need to be resized even if this widget doesn't.  For 
        # example, consider a container that takes up the whole window.  It's 
        # size won't change when a widget is added or removed from it, but it's 
        # children will still need to be resized.
        if self._num_children > 0:
            self.do_resize_children()

        # Try to redraw the widget.  This won't do anything if the widget isn't 
        # ready to draw.
        self.draw()

    def regroup(self, new_group):
        """
        Change the pyglet graphics group associated with this widget.
        """
        # Changing the group is often an expensive operation, so don't do 
        # anything unless we have to.  It is assumed that do_regroup_children() 
        # depends only of self._group, so if self._group doesn't change, 
        # self.do_regroup_children() doesn't need to be called.
        if self._group is None or self._group != new_group:
            self._group = new_group
            self.do_regroup()

            if self._num_children > 0:
                self.do_regroup_children()

        # Try to redraw the widget.  This won't do anything if the widget 
        # isn't ready to draw.
        self.draw()

    def hide(self):
        if self.is_visible:
            self.ungrab_mouse()
            self.undraw()
        self._is_hidden = True
        self._hide_children()

    def unhide(self, draw=True):
        self._is_hidden = False
        if self.is_visible and draw:
            self.draw()
        self._unhide_children(draw)

    def draw(self):
        """
        In order for a widget to be drawn, four conditions need to be met:

        1. The widget must be connected to the root of the widget hierarchy.  
           Widgets get their pyglet batch object from the root widget, so 
           without this connection they cannot be drawn.

        2. The widget must have a size specified by its ``rect`` attribute.  
           This attribute is set when the widget is attached to the hierarchy 
           and its parent calls its ``resize()`` method.

        3. The widget must be associated with a pyglet graphics group, which 
           controls things like how the widget will be stacked or scrolled.  A 
           group is set when the widget is attached to the hierarchy and its 
           parent calls its ``regroup()`` method.

        4. The widget must not be hidden.
        """
        if self.root is None: return
        if self.rect is None: return
        if self.group is None: return
        if self.is_hidden: return

        self.do_draw()

    def draw_all(self):
        self.draw()
        for child in self.__children:
            child.draw_all()

    def undraw(self):
        self.do_undraw()

    def undraw_all(self):
        self.undraw()

        for child in self.__children:
            child.undraw_all()

    def do_attach(self):
        """
        React to the widget being attached to the GUI.

        Specifically, this method is called when the widget becomes connected, 
        through any number of parent widgets, the root of the widget hierarchy.  
        When this happens, ``self.root`` will return a widget rather than None.
        
        Note that this method will not necessarily be called when the widget is 
        simply added to a parent widget.  If the parent is already attached to 
        the GUI itself, then this method will be called right then.  Otherwise, 
        this method will be called when that parent (or one of its parents) is 
        attached to the GUI.

        This method is mainly useful for widgets that need to take control away 
        from the root widget for some reason.  For example, Viewport widgets 
        override how mouse events are interpreted and Dialog widgets grab all 
        the key and mouse events for themselves.
        """
        pass

    def do_detach(self):
        """
        React to the widget being detached from the GUI.
        """
        pass

    def do_claim(self):
        # If the widget only has one child, then it probably makes sense to 
        # just claim enough space for that child.  Otherwise force the subclass 
        # to provide an implementation.
        if self._num_children == 1:
            return next(iter(self.__children)).claimed_size
        else:
            raise NotImplementedError

    def do_resize(self):
        """
        React to a change in the widget's size.

        Only widgets that actually draw things need to implement this method.  
        If the widget has children widgets that it may need to redistribute 
        space between, it should do that is do_resize_children().

        However, keep in mind that this method is called before the widget is 
        drawn and may be called after it's been undrawn, so any vertex lists 
        created in the draw function may or may not exist yet/anymore.  If 
        those vertex lists don't exist yet, there's nothing this function needs 
        to do.  The ``draw()`` function will be called when the widget's ready 
        to draw, and at that point the vertex lists should be created with the 
        right size and shape.
        """
        pass

    def do_resize_children(self):
        """
        React to changes that might require this widget's children to be 
        resized.

        This method is called when the widget's own size is changed or when 
        children are attached to or detached from the widget.  A typical 
        implementation would iterate through all the children attached to the 
        widget and call ``resize()`` on each one.
        """
        for child in self.__children:
            child.resize(self.rect)

    def do_regroup(self):
        """
        React to a change in the widget's pyglet graphics group.

        In pyglet, groups are used to control layers and OpenGL state.  This 
        method is called whenever the widget's group is changed, for example 
        when the widget is attached to the GUI or moved from one part 
        of the GUI to another.

        Only widgets that actually draw things need to implement this method, 
        because groups aren't used for anything but drawing.  Widgets that 
        contain other widgets may need to implement ``do_regroup_children()`` 
        to describe how those children should be regrouped.

        It's not always trivial to change the group used to draw something in 
        pyglet.  The way to do this depends on what's being drawn and whether 
        or not it's been drawn before.  The simplest case are high-level APIs 
        like ``pyglet.sprite.Sprite`` that allow you to simply change a 
        ``group`` attribute.  On the other hand, if you're drawing vertex lists 
        yourself, you need to call the ``Batch.migrate()`` method.  This method 
        needs to know the OpenGL mode (e.g. GL_QUADS) associated with the 
        vertex list, so you will have to keep track of that.

        Keep in mind that this method is called before the widget is drawn and 
        may be called after it's been undrawn, so any vertex lists created in 
        the draw function may or may not exist yet/anymore.  If those vertex 
        lists don't exist yet, there's nothing this function needs to do.  The 
        ``draw()`` function will be called when the widget's ready to draw, and 
        at that point the vertex lists should be created with the right group.
        """
        self.undraw()

    def do_regroup_children(self):
        """
        React to changes that might require this widget's children to be 
        regrouped.

        This method is called when the widget's own group is changed or when 
        children are attached to or detached from the widget.  A typical 
        implementation would iterate through all the children attached to the 
        widget and call ``regroup()`` on each one.  The default implementation 
        puts all the children in the same group as the widget itself.
        """
        for child in self.__children:
            child.regroup(self.group)

    def do_draw(self):
        """
        Draw any shapes or images associated with this widget.

        This method is called by ``draw()`` after it checks to make sure the 
        widget is attached to the root of the GUI hierarchy and that the 
        ``rect``, ``group``, and ``batch`` attributes have all been set.  

        This method is called both to draw the widget for the first time and to 
        update it subsequently.  This usually means that you need to check to 
        see if your graphics objects and resources need to be initialized yet.
        """
        pass

    def do_undraw(self):
        """
        This method may be called before draw().
        """
        pass

    def do_find_children_under_mouse(self, x, y):
        """
        Yield all the children under the given mouse coordinate.

        The order in which the children are yielded is arbitrary.  It's ok to 
        return children that are hidden; they will be filtered out later.  
        """
        yield from (w for w in self.__children if w.is_under_mouse(x, y))

    def on_mouse_press(self, x, y, button, modifiers):
        children_under_mouse = self._find_children_under_mouse(x, y)

        for child in children_under_mouse.current:
            child.dispatch_event('on_mouse_press', x, y, button, modifiers)

        self.start_event('on_mouse_hold')

    def on_mouse_release(self, x, y, button, modifiers):
        children_under_mouse = self._find_children_under_mouse(x, y)

        for child in children_under_mouse.current:
            child.dispatch_event('on_mouse_release', x, y, button, modifiers)

        self.stop_event('on_mouse_hold')

    def on_mouse_motion(self, x, y, dx, dy):
        children_under_mouse = self._find_children_under_mouse(x, y)

        for child in children_under_mouse.exited:
            child.dispatch_event('on_mouse_leave', x, y)

        for child in children_under_mouse.entered:
            child.dispatch_event('on_mouse_enter', x, y)

        for child in children_under_mouse.current:
            child.dispatch_event('on_mouse_motion', x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        children_under_mouse = self._find_children_under_mouse(x, y)

        for child in children_under_mouse.entered:
            child.dispatch_event('on_mouse_enter', x, y)

    def on_mouse_leave(self, x, y):
        # We have to actually check which widgets are still "under the mouse" 
        # to correctly handle widgets that are grabbing the mouse when the 
        # mouse leaves the window.
        children_under_mouse = self._find_children_under_mouse_after_leave()

        for child in children_under_mouse.exited:
            child.dispatch_event('on_mouse_leave', x, y)

        self.stop_event('on_mouse_hold')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        children_under_mouse = self._find_children_under_mouse(x, y)

        for child in children_under_mouse.exited:
            child.dispatch_event('on_mouse_drag_leave', x, y)

        for child in children_under_mouse.entered:
            child.dispatch_event('on_mouse_drag_enter', x, y)

        for child in children_under_mouse.current:
            child.dispatch_event('on_mouse_drag', x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        children_under_mouse = self._find_children_under_mouse(x, y)

        for child in children_under_mouse.entered:
            child.dispatch_event('on_mouse_drag_enter', x, y)

    def on_mouse_drag_leave(self, x, y):
        # We have to actually check which widgets are still "under the mouse" 
        # to correctly handle widgets that are grabbing the mouse when the 
        # mouse leaves the window.
        children_under_mouse = self._find_children_under_mouse_after_leave()

        for child in children_under_mouse.exited:
            child.dispatch_event('on_mouse_drag_leave', x, y)

        self.stop_event('on_mouse_hold')

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        children_under_mouse = self._find_children_under_mouse(x, y)
        for child in children_under_mouse.current:
            child.dispatch_event('on_mouse_scroll', x, y, scroll_x, scroll_y)

    def grab_mouse(self):
        if self.parent is self:
            return

        if self.parent._mouse_grabber is not None:
            grabber = self.root._find_mouse_grabber()
            raise UsageError(f"{grabber} is already grabbing the mouse, {self} can't grab it.")

        self.parent._mouse_grabber = self
        self.parent.grab_mouse()

    def ungrab_mouse(self):
        if self.parent is None: return
        if self.parent is self: return

        if self.parent._mouse_grabber is self:
            self.parent._mouse_grabber = None
            self.parent.ungrab_mouse()

    def get_parent(self):
        return self._parent

    def get_root(self):
        return self._root

    def get_window(self):
        return self.root.window if self.is_attached_to_gui else None

    def get_batch(self):
        return self.root.batch if self.is_attached_to_gui else None

    def get_group(self):
        return self._group

    def get_rect(self):
        return self._rect

    def get_size_hint(self):
        return self._width_hint, self._height_hint

    def set_size_hint(self, new_width, new_height):
        self._width_hint = new_width
        self._height_hint = new_height
        self.repack()

    size_hint = property(
            get_size_hint, lambda self, size: self.set_size_hint(*size))

    def get_width_hint(self):
        return self._width_hint

    def set_width_hint(self, new_width):
        self._width_hint = new_width
        self.repack()

    def get_height_hint(self):
        return self._height_hint

    def set_height_hint(self, new_height):
        self._height_hint = new_height
        self.repack()

    def get_claimed_rect(self):
        return Rect.from_size(self._claimed_width, self._claimed_height)

    def get_claimed_size(self):
        return self._claimed_width, self._claimed_height

    def get_claimed_width(self):
        return self._claimed_width

    def get_claimed_height(self):
        return self._claimed_height

    def get_padded_rect(self):
        return self._padded_rect

    def get_padding(self):
        return (self._left_padding, self._right_padding,
                self._top_padding, self._bottom_padding)

    def set_padding(self, all=None, *, horz=None, vert=None,
            left=None, right=None, top=None, bottom=None):
        self._set_padding(all, horz, vert, left, right, top, bottom)
        self.repack()

    padding = late_binding_property(get_padding, set_padding)

    def get_horz_padding(self):
        return self._left_padding, self._right_padding

    def set_horz_padding(self, new_padding):
        self._left_padding = new_padding
        self._right_padding = new_padding
        self.repack()

    def get_vert_padding(self):
        return self._top_padding, self._bottom_padding

    def set_vert_padding(self, new_padding):
        self._top_padding = new_padding
        self._bottom_padding = new_padding
        self.repack()

    def get_left_padding(self):
        return self._left_padding

    def set_left_padding(self, new_padding):
        self._left_padding = new_padding
        self.repack()

    def get_right_padding(self):
        return self._right_padding

    def set_right_padding(self, new_padding):
        self._right_padding = new_padding
        self.repack()

    def get_top_padding(self):
        return self._top_padding

    def set_top_padding(self, new_padding):
        self._top_padding = new_padding
        self.repack()

    def get_bottom_padding(self):
        return self._bottom_padding

    def set_bottom_padding(self, new_padding):
        self._bottom_padding = new_padding
        self.repack()

    def get_total_padding(self):
        return self.total_horz_padding, self.total_vert_padding

    def get_total_horz_padding(self):
        return self._left_padding + self._right_padding

    def get_total_vert_padding(self):
        return self._top_padding + self._bottom_padding

    def get_alignment(self):
        return self._alignment

    def set_alignment(self, new_alignment):
        self._alignment = new_alignment
        self.repack()

    @property
    def is_hidden(self):
        return self._is_hidden or self._is_parent_hidden

    @property
    def is_visible(self):
        return not self.is_hidden

    @property
    def is_attached_to_gui(self):
        return self.root is not None

    def is_under_mouse(self, x, y):
        if self.rect is None:
            return False
        return (x, y) in self.rect

    def debug_drawing_problems(self):
        """
        Suggest reasons why a widget is not displaying.

        It can be hard to debug problems when nothing is showing up on the 
        screen, so this method is meant to help look for common reasons why 
        that might be the case.
        """
        diagnoses = []

        # If the widget isn't attached to the GUI, figure out which parent is 
        # the problem.

        if not self.is_attached_to_gui:

            def find_unattached_parent(widget, level=0):
                if widget.parent is None: return widget, level
                if widget.parent is self.root: return widget, level
                else: return find_unattached_parent(widget.parent, level + 1)

            try:
                unattached_parent, level = find_unattached_parent(self)
            except RecursionError:
                diagnoses.append("{self} seems to have an infinite number of parents.\nCheck for circular references between its parents.")
            else:
                if unattached_parent is self:
                    diagnoses.append("{self} is not attached to the GUI.")
                else:
                    diagnoses.append("{unattached_parent}, a widget {level} level(s) above {self}, is not attached to the GUI.")

        # If the widget is attached to the GUI, make sure the widget is fully 
        # configured (i.e. rect and group are set) and not hidden.

        else:
            if self.rect is None:
                diagnoses.append("{self} was not given a size by its parent.\nCheck for bugs in {self.parent.__class__.__name__}.do_resize_children()")

            elif self.rect.area == 0:
                if self.claimed_width and self.claimed_height:
                    diagnoses.append("{self} requested {self.claimed_width}x{self.claimed_height} but was given {self.rect.width}x{self.rect.height}.\nCheck for bugs in {self.parent.__class__.__name__}.do_resize_children()")
                else:
                    diagnoses.append("{self} was given no space because it requested {self.claimed_width}x{self.claimed_height}.\nCheck for bugs in {self.__class__.__name__}.do_claim()")

            if self.group is None:
                diagnoses.append("{self} was not given a group by its parent.\nCheck for bugs in {self.parent.__class__.__name__}.do_regroup_children()")

            if self.is_hidden:

                def find_hidden_parent(widget, level=0):
                    if widget._hidden: return widget, level
                    else: return find_hidden_parent(widget.parent, level + 1)

                hidden_parent, level = find_hidden_parent(self)

                if hidden_parent is self:
                    diagnoses.append("{self} is hidden.\nCall {self.__class__.__name__}.unhide() to reveal it.")
                else:
                    diagnoses.append("{hidden_parent}, a widget {level} level(s) above {self}, is hidden.\nCall {hidden_parent.__class__.__name__}.unhide() to reveal it and its children.")

        # If no problems were found, say so.

        if not diagnoses:
            diagnoses.append("{self} seems to have been drawn.\nCheck for bugs in {self.__class__.__name__}.do_draw()")

        # Print out the diagnoses.

        def join(items, sep):
            for i, item in enumerate(items):
                if i < len(items) - 1:
                    yield item, sep
                else:
                    yield item, ''

        for diagnosis, sep in join(diagnoses, '\n'):
            print(diagnosis.format(**locals()) + sep, flush=True)

    def debug_placement_problems(self, claimed='red', assigned='green',
            content='blue'):
        """
        Draw boxes showing the widgets assigned, claimed, and content rects.
        """
        if not self.is_attached_to_gui:
            raise UsageError("the widget must be attached to the GUI to debug placement problems.")

        group = pyglet.graphics.OrderedGroup(1)

        drawing.Outline(
            rect=self.claimed_rect,
            color=claimed,
            batch=self.batch,
            group=group,
        )
        drawing.Outline(
            rect=self._assigned_rect,
            color=assigned,
            batch=self.batch,
            group=group,
        )
        drawing.Outline(
            rect=self.rect,
            color=content,
            batch=self.batch,
            group=group,
        )

    def _attach_child(self, child):
        """
        Add a child to this widget.

        This method checks to make sure the child isn't already attached to 
        some other widget, tells the child who it's new parent is, and adds the 
        child to an internal list of children widgets.

        This method is only meant to be called in subclasses of Widget, which 
        is why it's prefixed with an underscore.
        """
        if not isinstance(child, Widget):
            raise UsageError(f"{child} is not a widget, did you forget to inherit from something?")

        if child.parent is self:
            return child

        if child.parent is not None:
            raise UsageError(f"{child} is already attached to {child.parent}, cannot attach to {self}")

        child._parent = self
        self.__children.add(child)

        if self.is_attached_to_gui:
            for widget in child._yield_self_and_all_children():
                widget._root = self.root
                widget.do_attach()

        if self.is_hidden:
            self._hide_children()
        else:
            self._unhide_children(False)

        self.dispatch_event('on_add_child', child)
        return child

    def _detach_child(self, child):
        """
        Detach a child from this widget.

        This method checks to make sure the child is currently attached to this 
        widget, undraws the child, resets several of the child's attributes 
        that might have been set by this widget, and removes the child from an 
        internal list of children widgets.
        
        This method is only meant to be called in subclasses of Widget, which 
        is why it's prefixed with an underscore.
        """
        if child.parent is not self:
            raise UsageError('{} is attached to {}, cannot detach from {}.'.format(child, child._parent, self))

        for widget in child._yield_self_and_all_children():
            widget.do_detach()
            widget.ungrab_mouse()
            widget.undraw()
            widget._root = None

        self.__children.discard(child)
        child._parent = None

        # Set the detached child's ``group`` and ``rect`` attributes to None, 
        # so that its new parent will have to supply them before the child can 
        # be drawn again.
        child._group = None
        child._rect = None

        # Let the user react to a child being attached.
        self.dispatch_event('on_remove_child', child)

        # Derived classes are expected to call _repack_and_regroup_children() 
        # after this method.
        return child

    @update_function
    def _repack_and_regroup_children(self):
        """
        Resize and regroup the children of this widget if this widget is 
        already attached to the GUI.  Otherwise, don't do anything.

        Container widgets should call this method whenever a new child widget 
        is attached.  

        Before a widget is attached to the GUI, it can't have a size or a group 
        because these attributes derive from a parent widget.  If any children 
        are attached to the widget at this point, they cannot be given sizes or 
        groups for the same reason.  Once the widget is attached to the GUI, it 
        will be given a size and a group by its parent, then it will give sizes 
        and groups to the children already attached to it.  If any children are 
        attached after this point, they should be given a size and group right 
        away.

        Note that what happens when a child widget is attached to its parent 
        depends on whether the parent is already attached to the GUI or not.  
        If it is, the child is resized and regrouped (other children may be 
        resized and regrouped at the same time).  Otherwise, nothing happens.  
        This method handles this logic.  As long as container subclasses call 
        this method each time a child is added or removed, their children will 
        be properly sized and grouped no matter when they were attached.
        """
        if self.is_attached_to_gui:
            self.repack()
            if self._num_children > 0:
                self.do_regroup_children()

    def _hide_children(self):
        for child in self._yield_all_children():
            if child.is_visible:
                child.ungrab_mouse()
                child.undraw()

            child._is_parent_hidden = True

    def _unhide_children(self, draw=True):

        def unhide_child(child):
            # Indicate that this child's parent is no longer hidden.
            child._is_parent_hidden = False

            # If the child itself isn't hidden:
            if child.is_visible:

                # Draw the widget unless the caller asked not to.
                if draw:
                    child.draw()

                # Recursively unhide the child's children.
                for grandchild in child.__children:
                    unhide_child(grandchild)

        for child in self.__children:
            unhide_child(child)

    def _yield_all_children(self):
        for child in self.__children:
            yield from child._yield_self_and_all_children()

    def _yield_self_and_all_children(self):
        yield self
        yield from self._yield_all_children()

    def _find_children_under_mouse(self, x, y):
        previously_under_mouse = self._children_under_mouse

        if self._mouse_grabber is not None:
            self._children_under_mouse = {self._mouse_grabber}
        else:
            self._children_under_mouse = {
                    w for w in self.do_find_children_under_mouse(x, y)
                    if w.is_visible
            }

        return Widget._ChildrenUnderMouse(
                previously_under_mouse, self._children_under_mouse)

    def _find_children_under_mouse_after_leave(self):
        previously_under_mouse = self._children_under_mouse

        if self._mouse_grabber is not None:
            self._children_under_mouse = {self._mouse_grabber}
        else:
            self._children_under_mouse = set()

        return Widget._ChildrenUnderMouse(
                previously_under_mouse, self._children_under_mouse)

    def _find_mouse_grabber(self):
        """
        Return the widget grabbing the mouse from this widget, or None if the 
        mouse isn't being grabbed.  
        
        Note that unless this method is being called on the root widget, some 
        widget elsewhere in the hierarchy may still be grabbing the mouse even 
        if this returns None.
        """

        if self._mouse_grabber is None:
            return None

        def recursive_find(parent):
            grabber = parent._mouse_grabber
            return parent if grabber is None else recursive_find(grabber)

        return recursive_find(self)

    def _get_num_children(self):
        return len(self.__children)

    _num_children = property(_get_num_children)

    def _set_padding(self, all=None, horz=None, vert=None,
            left=None, right=None, top=None, bottom=None):
        """
        Set the four padding attributes (top, left, bottom, right) defined in 
        the Widget class and don't repack.  This method is provided to help the 
        Widget constructor initialize its default paddings without calling and 
        polymorphic methods.
        """
        self._left_padding = first_not_none((left, horz, all, 0))
        self._right_padding = first_not_none((right, horz, all, 0))
        self._top_padding = first_not_none((top, vert, all, 0))
        self._bottom_padding = first_not_none((bottom, vert, all, 0))


    class _ChildrenUnderMouse:

        def __init__(self, previous, current):
            self._previous = previous
            self._current = current

        @property
        def previous(self):
            return self._previous

        @property
        def current(self):
            return self._current

        @property
        def entered(self):
            return self.current - self.previous

        @property
        def unchanged(self):
            return self.current & self.previous

        @property
        def exited(self):
            return self.previous - self.current


Widget.register_event_type('on_add_child')
Widget.register_event_type('on_remove_child')
Widget.register_event_type('on_mouse_press')
Widget.register_event_type('on_mouse_release')
Widget.register_event_type('on_mouse_hold')
Widget.register_event_type('on_mouse_motion')
Widget.register_event_type('on_mouse_enter')
Widget.register_event_type('on_mouse_leave')
Widget.register_event_type('on_mouse_drag')
Widget.register_event_type('on_mouse_drag_enter')
Widget.register_event_type('on_mouse_drag_leave')
Widget.register_event_type('on_mouse_scroll')

