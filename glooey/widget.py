import pyglet
import autoprop
from vecrec import Rect
from debugtools import p, pp, pv
from . import drawing
from .helpers import *

@autoprop
class Widget (pyglet.event.EventDispatcher, HoldUpdatesMixin):
    default_padding = None
    default_horz_padding = None
    default_vert_padding = None
    default_left_padding = None
    default_right_padding = None
    default_top_padding = None
    default_bottom_padding = None
    default_alignment = 'fill'

    def __init__(self):
        pyglet.event.EventDispatcher.__init__(self)
        HoldUpdatesMixin.__init__(self)

        self._parent = None
        # Use a double-underscore to avoid name conflicts; `_children` is a 
        # useful name for subclasses, so I don't want it to cause conflicts.
        self.__children = set()
        self._children_under_mouse = set()
        self._children_can_overlap = True
        self._group = None
        self._rect = None
        self._content_width = 0
        self._content_height = 0
        self._claimed_width = 0
        self._claimed_height = 0
        self._assigned_rect = None
        self._is_hidden = False
        self._is_claim_stale = True
        self._spurious_leave_event = False

        # Take care to avoid calling any potentially polymorphic methods, such 
        # as set_padding() or repack().  When these methods are overridden, 
        # they often become dependent on the overriding subclass being properly
        # initialized.  Since that hasn't happened by the time this constructor 
        # is called, these polymorphic methods can cause headaches.
        self._set_padding(
                all=self.default_padding,
                horz=self.default_horz_padding,
                vert=self.default_vert_padding,
                left=self.default_left_padding,
                right=self.default_right_padding,
                top=self.default_top_padding,
                bottom=self.default_bottom_padding,
        )
        self._set_alignment(
                self.default_alignment)

    def __repr__(self):
        return '{}(id={})'.format(
                self.__class__.__name__,
                hex(id(self))[-4:],
        )

    def __iter__(self):
        yield from self.__children

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
        if not self._is_claim_stale:
            return False

        # Have each child widget claim space for itself, so this widget can 
        # take those space requirements into account.
        for child in self.__children:
            child.claim()

        # Make note of the previous claim, so we can say whether or not it has 
        # changed.
        previous_claim = self._claimed_width, self._claimed_height

        # Keep track of the amount of space the widget needs for itself 
        # (content) and for itself in addition to its padding (claim).
        self._min_width, self._min_height = self.do_claim()
        self._claimed_width = \
                self._min_width + self._left_padding + self._right_padding
        self._claimed_height = \
                self._min_height + self._top_padding + self._bottom_padding

        # Return whether or not the claim has changed since the last repack.  
        # This determines whether the widget's parent needs to be repacked.
        return previous_claim != (self._claimed_width, self._claimed_height)

    def resize(self, new_rect):
        """
        Change the size or shape of this widget.

        This method is triggered by repack(), which recursively climbs the 
        widget hierarchy to make space for the widgets that need it, then calls 
        resize() on any widget that need to adapt to the new space allocation.
        """
        self._assigned_rect = new_rect
        self.realign()

    def realign(self):
        # Subtract padding from the full amount of space assigned to this 
        # widget.
        padded_rect = self._assigned_rect.copy()
        padded_rect.left += self._left_padding
        padded_rect.bottom += self._bottom_padding
        padded_rect.width -= self._left_padding + self._right_padding
        padded_rect.height -= self._top_padding + self._bottom_padding

        # Align this widget within the space available to it (i.e. the assigned 
        # space minus the padding).
        content_rect = Rect.from_size(self._min_width, self._min_height)
        self._alignment_func(content_rect, padded_rect)
        content_rect.round()

        # Guarantee that do_resize() is only called if the size of the widget 
        # actually changed.  This is probably doesn't have a significant effect 
        # on performance, but hopefully it gives people reimplementing 
        # do_resize() less to worry about.
        if self._rect is None or self._rect != content_rect:
            self._rect = content_rect
            self.do_resize()

        # The children may need to be resized even if this widget doesn't.  For 
        # example, consider a container that takes up the whole window.  It's 
        # size won't change when a widget is added or removed from it, but it's 
        # children will still need to be resized.
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
            self.do_regroup_children()

        # Try to redraw the widget.  This won't do anything if the widget 
        # isn't ready to draw.
        self.draw()

    def hide(self):
        if self.is_visible:
            self.undraw_all()
        self._is_hidden = True

    def unhide(self, draw=True):
        self._is_hidden = False
        if self.is_visible and draw:
            self.draw_all()

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

        It's ok to return children that are hidden; these will be filtered out 
        later.
        """

        visible_children = {x for x in self.__children if x.is_visible}

        def yield_previous_children_then_others():
            yield from visible_children & self._children_under_mouse
            yield from visible_children - self._children_under_mouse

        for child in yield_previous_children_then_others():
            if child.is_under_mouse(x, y):
                yield child

                # If a widget can guarantee that none of its children overlap, 
                # it can speed up this method by aborting the search as soon as 
                # the first widget under the mouse is found.  Since the widgets 
                # that were previously under the mouse are checked first, this 
                # makes the search constant-time in most cases.

                if not self._children_can_overlap:
                    break

    def on_mouse_press(self, x, y, button, modifiers):
        for child in self._children_under_mouse:
            child.dispatch_event('on_mouse_press', x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for child in self._children_under_mouse:
            child.dispatch_event('on_mouse_release', x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        under_mouse, previously_under_mouse = \
                self._find_children_under_mouse(x, y)

        for child in previously_under_mouse:
            if child not in under_mouse:
                child.dispatch_event('on_mouse_leave', x, y)

        for child in under_mouse:
            if child not in previously_under_mouse:
                child.dispatch_event('on_mouse_enter', x, y)

            child.dispatch_event('on_mouse_motion', x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        # For some reason, whenever the mouse is clicked, pyglet generates a 
        # on_mouse_leave event followed by a on_mouse_enter event.  There's no 
        # way to tell whether or not that happened in this handler alone, so we 
        # check a flag that would be set in on_mouse_leave() if a spurious 
        # event was detected.  If the event is spurious, reset the flag, ignore 
        # the event, and stop it from propagating.
        if self._spurious_leave_event:
            self._spurious_leave_event = False
            return True

        under_mouse, previously_under_mouse = \
                self._find_children_under_mouse(x, y)
        assert not previously_under_mouse

        for child in under_mouse:
            child.dispatch_event('on_mouse_enter', x, y)

    def on_mouse_leave(self, x, y):
        # For some reason, whenever the mouse is clicked, pyglet generates a 
        # on_mouse_leave event followed by a on_mouse_enter event.  We can tell 
        # that this is happening in this handler because the mouse coordinates 
        # will still be under the widget.  In this case, set a flag so 
        # on_mouse_enter() will know to ignore the spurious event to follow, 
        # ignore the event, and stop it from propagating.
        if self.is_under_mouse(x, y):
            self._spurious_leave_event = True
            return True

        for child in self._children_under_mouse:
            child.dispatch_event('on_mouse_leave', x, y)

        self._children_under_mouse = set()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        under_mouse, previously_under_mouse = \
                self._find_children_under_mouse(x, y)

        for child in previously_under_mouse:
            if child not in under_mouse:
                child.dispatch_event('on_mouse_drag_leave', x, y)

        for child in under_mouse:
            if child not in previously_under_mouse:
                child.dispatch_event('on_mouse_drag_enter', x, y)

            child.dispatch_event(
                    'on_mouse_drag', x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        under_mouse, previously_under_mouse = \
                self._find_children_under_mouse(x, y)

        assert not previously_under_mouse

        for child in under_mouse:
            child.dispatch_event('on_mouse_drag_enter', x, y)

    def on_mouse_drag_leave(self, x, y):
        for child in self._children_under_mouse:
            child.dispatch_event('on_mouse_leave', x, y)
        self._children_under_mouse = set()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for child in self._children_under_mouse:
            child.dispatch_event('on_mouse_scroll', x, y, scroll_x, scroll_y)

    def get_parent(self):
        return self._parent

    def get_root(self):
        return self.parent.root if self.parent is not None else None

    def get_window(self):
        return self.root.window if self.is_attached_to_gui else None

    def get_batch(self):
        return self.root.batch if self.is_attached_to_gui else None

    def get_group(self):
        return self._group

    def get_rect(self):
        return self._rect

    def get_claimed_rect(self):
        return Rect.from_size(self._claimed_width, self._claimed_height)

    def get_claimed_size(self):
        return self._claimed_width, self._claimed_height

    def get_claimed_width(self):
        return self._claimed_width

    def get_claimed_height(self):
        return self._claimed_height

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

    def get_alignment(self):
        return self._alignment_func

    def set_alignment(self, new_alignment):
        self._set_alignment(new_alignment)
        self.repack()

    @property
    def is_hidden(self):
        if self.parent is None:
            return self._is_hidden
        else:
            return self._is_hidden or self.parent.is_hidden

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
                diagnoses.append("{self} reqested (and was given) no space.\nCheck for bugs in {self.__class__.__name__}.do_claim()")

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

    def debug_placement_problems(self, claimed='red', assigned='green', content='blue'):
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
                widget.do_attach()

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

        child.undraw_all()
        self.__children.discard(child)
        child._parent = None

        # Set the detached child's ``group`` and ``rect`` attributes to None, 
        # so that its new parent will have to supply them before the child can 
        # be drawn again.
        child._group = None
        child._rect = None

        # Let the user react to a child being attached.
        self.dispatch_event('on_remove_child', child)

        # Derived classes are expected to call _resize_and_regroup_children() 
        # after this method.
        return child

    @update_function
    def _resize_and_regroup_children(self):
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
            self.do_regroup_children()

    def _yield_self_and_all_children(self):
        yield self
        for child in self.__children:
            yield from child._yield_self_and_all_children()

    def _find_children_under_mouse(self, x, y):
        # This method returns a set, but maybe it should return a list?  
        # z-order is important, but maybe that's something for the specific 
        # parent classes to worry about?

        previously_under_mouse = self._children_under_mouse
        self._children_under_mouse = {
                w for w in self.do_find_children_under_mouse(x, y)
                if w.is_visible}

        return self._children_under_mouse, previously_under_mouse

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

    def _set_alignment(self, new_alignment):
        """
        Set the alignment attribute and don't repack.  This method is provided 
        to help the Widget constructor initialize its default paddings without 
        calling and polymorphic methods.
        """
        self._alignment_func = drawing.cast_to_alignment(new_alignment)


Widget.register_event_type('on_add_child')
Widget.register_event_type('on_remove_child')
Widget.register_event_type('on_mouse_press')
Widget.register_event_type('on_mouse_release')
Widget.register_event_type('on_mouse_motion')
Widget.register_event_type('on_mouse_enter')
Widget.register_event_type('on_mouse_leave')
Widget.register_event_type('on_mouse_drag')
Widget.register_event_type('on_mouse_drag_enter')
Widget.register_event_type('on_mouse_drag_leave')
Widget.register_event_type('on_mouse_scroll')

