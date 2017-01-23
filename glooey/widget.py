import pyglet
import autoprop
from vecrec import Rect
from pprint import pprint
from .helpers import *

@autoprop
class Widget (pyglet.event.EventDispatcher, HoldUpdatesMixin):

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
        self._hidden = False
        self._is_claim_stale = True
        self._spurious_leave_event = False
        self._draw_status = 'never drawn'
        self._min_width = 0
        self._min_height = 0

    def __repr__(self):
        return '{}(id={})'.format(
                self.__class__.__name__,
                hex(id(self))[-4:],
        )

    @update_function
    def repack(self):
        if not self.is_attached_to_gui:
            return

        self.claim()

        # If the widget is either too big or too small, repack its parent to 
        # make more space.
        if self.rect.size != self.min_size:
            self._is_claim_stale = False
            self.parent.repack()
            self._is_claim_stale = True

        # Otherwise, stop recursing and resize the widget's children.
        else:
            self.do_resize_children()
            self.draw()

    def claim(self):
        if self._is_claim_stale:
            # Have each child widget claim space for itself, so this widget can 
            # take those space requirements into account.
            for child in self.__children:
                child.claim()

            # Claim space for this widget.
            self._min_width, self._min_height = self.do_claim()

    def resize(self, new_rect):
        """
        Change the size or shape of this widget.

        This method is triggered by repack(), which recursively climbs the 
        widget hierarchy to make space for the widgets that need it, then calls 
        resize() on any widget that need to adapt to the new space allocation.
        """
        if self._rect is None or self._rect != new_rect:
            self._rect = new_rect
            self.do_resize()

        # Even if this widget didn't change size, it may be that the children 
        # need to move or be rearranged.  This came up for me with a custom 
        # placement function, but I can imagine other scenarios as well.
        self.do_resize_children()

        # Try to redraw the widget.  This won't do anything if the widget isn't 
        # ready to draw.
        self.draw()

    def regroup(self, new_group):
        """
        Change the pyglet graphics group associated with this widget.
        """
        if self._group is None or self._group != new_group:
            self._group = new_group

            self.do_regroup()
            self.do_regroup_children()

        # Try to redraw the widget.  This won't do anything if the widget 
        # isn't ready to draw.
        self.draw()

    def hide(self):
        self._hidden = True
        self.undraw_all()

    def unhide(self):
        self._hidden = False
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

        If these conditions are not met, the widget not be drawn and a debug- 
        level log message explaining why will be issued.
        """

        # If the widget can't be rendered for some reason, log a debug-level 
        # message describing why.  It can be really hard to figure out why 
        # something isn't showing up on the screen at all, and this will help 
        # if the user thinks to turn on logging.
        #
        # The reason I'm issuing debug messages instead of errors is that these 
        # checks are expected to fail during routine operations.  For example, 
        # if a parent calls resize() and then regroup() on a child, both calls 
        # will attempt to redraw the widget but the first will fail.

        self._draw_status = 'draw() called'

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
        self._draw_status = 'undraw() called'
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
        If the widget has children widgets that it may needs to redistribute 
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

    @property
    def is_hidden(self):
        return self._hidden

    @property
    def is_visible(self):
        return not self._hidden

    def get_min_width(self):
        return self._min_width

    def get_min_height(self):
        return self._min_height

    def get_min_size(self):
        return self._min_width, self._min_height

    def get_min_rect(self):
        return Rect.from_size(self._min_width, self._min_height)

    @property
    def is_attached_to_gui(self):
        return self.root is not None

    def is_under_mouse(self, x, y):
        if self.rect is None:
            return False
        return (x, y) in self.rect

    def diagnose_drawing_problems(self):
        """
        Suggest reasons why a widget is not displaying.

        It can be hard to debug problems when nothing is showing up on the 
        screen, so this method is meant to help look for common reasons why 
        that might be the case.

        The most common reason for a widget not being drawn is not being 
        attached to the root of the widget hierarchy (i.e. the GUI).  However, 
        there are also a number of ways to get bugs like this is you're writing 
        your own container widgets.
        """
        diagnoses = []

        if not self.is_attached_to_gui:

            # If the widget isn't attached to the GUI, figure out which parent 
            # is the problem.

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

        elif self._draw_status == 'draw() called':
            if self.rect is None:
                diagnoses.append("{self} was not given a size by its parent.\nThis is probably a bug in the parent widget.")

            if self.rect.area == 0:
                diagnoses.append("{self} reqested (and was given) no space.\nCheck for bugs in {self.__class__.__name__}.do_claim()")

            if self.group is None:
                diagnoses.append("{self} was not given a group by its parent.\nThis is probably a bug in the parent widget.")

            if self.is_hidden:
                diagnoses.append("{self} is currently hidden.\nUse the unhide() method to reveal it.")

            if not diagnoses:
                diagnoses.append("{self} seems to have been drawn.\nCheck for bugs in {self.__class__.__name__}.do_draw()")

        elif self._draw_status == 'undraw() called':
            diagnoses.append("{self} has not been drawn since it was last undrawn.")

        # Print out the diagnoses.

        def join(items, sep):
            for i, item in enumerate(items):
                if i < len(items) - 1:
                    yield item, sep
                else:
                    yield item, ''

        for diagnosis, sep in join(diagnoses, '\n'):
            print(diagnosis.format(**locals()) + sep, flush=True)

    def _attach_child(self, child):
        """
        Add a child to this widget.

        This method checks to make sure the child isn't already attached to 
        some other widget, tells the child who it's new parent is, and adds the 
        child to an internal list of children widgets.

        This method is only meant to be called in subclasses of Widget, which 
        is why it's prefixed with an underscore.
        """
        if child.parent is self:
            return child

        if child.parent is not None:
            raise UsageError('{} is already attached to {}, cannot attach to {}'.format(child, child.parent, self))

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

        visible_children = {x for x in self.__children if x.is_visible}
        previously_under_mouse = self._children_under_mouse
        self._children_under_mouse = set()

        def yield_previous_children_then_others():
            yield from visible_children & previously_under_mouse
            yield from visible_children - previously_under_mouse

        for child in yield_previous_children_then_others():
            if child.is_under_mouse(x, y):
                self._children_under_mouse.add(child)

                # If a widget can guarantee that none of its children overlap, 
                # it can speed up this method by aborting the search as soon as 
                # the first widget under the mouse is found.  Since the widgets 
                # that were previously under the mouse are checked first, this 
                # makes the search constant-time in most cases.

                if not self._children_can_overlap:
                    break

        return self._children_under_mouse, previously_under_mouse

    def _get_num_children(self):
        return len(self.__children)

    _num_children = property(_get_num_children)


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

