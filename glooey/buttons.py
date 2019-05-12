#!/usr/bin/env python3

"""
Widgets that react to being clicked on.
"""

import pyglet
import autoprop

from vecrec import Vector, Rect
from glooey import containers
from glooey.widget import Widget
from glooey.containers import Deck, Stack
from glooey.text import Label
from glooey.images import Image, Background
from glooey.helpers import *

@autoprop
class Rollover(Deck):
    custom_predicate = lambda self, w: True
    custom_rollover_state_priorities = {
            'base': 0,
            'over': 1,
            'down': 2,
            'off': 3,
    }

    def __init__(self, controller, initial_state, predicate=None, **states):
        super().__init__(initial_state, **states)
        self._controllers = [controller]
        self._predicate = predicate or self.custom_predicate

    def do_attach(self):
        for widget in self._controllers:
            self._add_handlers(widget)

        # Update the rollover state immediately; one of the controllers might 
        # be disabled.  See #25.
        self._update_state()

    def do_detach(self):
        for widget in self._controllers:
            self._remove_handlers(widget)

    def add_controller(self, widget):
        self._controllers.append(widget)
        self._add_handlers(widget)

    def remove_controller(self, widget):
        self._controllers.remove(widget)
        self._remove_handlers(widget)

    def get_predicate(self):
        return self._predicate

    def set_predicate(self, new_predicate):
        self._predicate = new_predicate

    def is_state_missing(self, state):
        if state not in self.known_states:
            return True
        else:
            widget = self.get_widget(state)
            return not self.predicate(widget)

    def _update_state(self, *ignored_event_args):
        state = 'base'
        priority = self.custom_rollover_state_priorities

        for widget in self._controllers:
            controller_state = \
                    widget.rollover_state if widget.is_enabled else 'off'
            if priority[controller_state] > priority[state]:
                state = controller_state

        state = self._substitute_missing_states(state)
        self.set_state(state)

    def _substitute_missing_states(self, state):
        if self.is_state_missing(state) and state == 'down':
            state = 'over'

        if self.is_state_missing(state) and state == 'over':
            state = 'base'

        return state

    def _add_handlers(self, widget):
        widget.push_handlers(
                on_rollover=self._update_state,
                on_enable=self._update_state,
                on_disable=self._update_state,
        )

    def _remove_handlers(self, widget):
        widget.remove_handlers(
                on_rollover=self._update_state,
                on_enable=self._update_state,
                on_disable=self._update_state,
        )


@autoprop
class Button(Widget):
    """
    A button has two layers:

    - Foreground (optional).
    - Rollover-responsive background.
    """
    Foreground = Label

    # Background should implement:
    # - is_empty(): Return true if the widget has nothing to display
    # - set_appearance(): Accept kwargs, change appearance accordingly.
    Background = Background
    Base = None
    Over = None
    Down = None
    Off = None

    custom_foreground_layer = 2
    custom_background_layer = 1
    custom_alignment = 'center'

    # These are provided for convenience.  If specified, the text/image 
    # attribute of the instantiated foreground widget will be set with the 
    # specified value.
    custom_text = None
    custom_image = None

    # There are also a bunch of dynamically generated/introspected custom 
    # attributes for setting "appearance" options on the background widgets.

    def __init__(self, *args, **kwargs):
        super().__init__()

        # Note that `Button` is basically a `Stack` with just two layers: 
        # foreground (optional) and background.  I decided to reimplement the 
        # stacking behavior---rather than using `Stack` internally---to keep 
        # the widget hierarchy as shallow as possible for this very commonly 
        # used widget.

        self._foreground = self.Foreground(*args, **kwargs) \
                if self.Foreground else None
        self._background = Rollover(
                self, 'base', predicate=lambda w: not w.is_empty)
        self._background.add_states(
                base = (self.Base or self.Background)(),
                over = (self.Over or self.Background)(),
                down = (self.Down or self.Background)(),
                off  = (self.Off  or self.Background)(),
        )

        if self.custom_text is not None:
            self._foreground.text = self.custom_text
        if self.custom_image is not None:
            self._foreground.image = self.custom_image

        self._init_custom_background_appearances()
        self._is_enabled = True

        if self._foreground is not None:
            self._attach_child(self._foreground)
        self._attach_child(self._background)

    def click(self):
        if self.is_enabled:
            self.dispatch_event('on_click')

    def do_claim(self):
        from .containers import claim_stacked_widgets
        return claim_stacked_widgets(*self._yield_layers())

    def do_resize_children(self):
        from .containers import align_widget_in_box
        for layer in self._yield_layers():
            align_widget_in_box(layer, self.rect)

    def do_regroup_children(self):
        from pyglet.graphics import OrderedGroup

        # Don't make unnecessary layers, see `Stack.do_regroup_children()`.

        if self._foreground is None:
            self._background._regroup(self.group)
        else:
            self._foreground._regroup(OrderedGroup(2, self.group))
            self._background._regroup(OrderedGroup(1, self.group))

    def get_foreground(self):
        return self._foreground
    
    def set_foreground(self, widget):
        if self._foreground is not None:
            self._detach_child(self._foreground)

        self._attach_child(self._foreground)
        self._foreground = widget
        self._repack_and_regroup_children()

    def del_foreground(self):
        if self._foreground is not None:
            self._foreground._detach_child(self._foreground)
            self._foreground = None
            self._repack_and_regroup_children()

    def set_background(self, **kwargs):
        """
        Set appearance options for any of the background widgets.

        This is a convenience method for calling `set_appearance()` on any of 
        the background widgets.  Each keyword argument to this function should 
        either be of the form `<rollover>` or `<rollover>_<kwarg>`, where 
        `<rollover>` is the name of a rollover state and `<kwargs>` is the 
        name of an argument to the `set_appearance()` method of the widget 
        representing that state.
        
        Arguments of the `<rollover>` form specify actual widgets to use for 
        the indicated state.  Arguments of the form `<rollover>_<kwarg>` 
        specify keyword arguments to pass to that widget's `set_appearance()` 
        method.  You can mix both kinds of arguments.
        
        The following rollover states are understood:

        - `base`
        - `over`
        - `down`
        - `off`

        The `<option>` names must be valid keyword arguments to the underlying 
        widget's `set_appearance()` method.  Of course, different widgets will 
        accept different arguments.  These arguments also require that the 
        background widgets implement the set_appearance()` method.  `Image` and 
        `Background` both meet this requirement, but widgets derived from other 
        classes may not.

        Note that any appearance options not specified will not be displayed.  
        In other words, if you only specify a base rollover state, the other 
        rollover states will be disabled.  Or if you only specify edge images, 
        no center images will be displayed.  A common mistake is to try to 
        configure the appearance of a button with multiple calls to this 
        method, but this will just result in the last call overriding all the 
        earlier ones.
        """
        rollover_states = self._background.known_states
        appearance_args = {k: {} for k in rollover_states}

        for key, arg in kwargs.items():
            tokens = key.split('_', 1)

            # Each keyword argument should begin with the name of one of the 
            # rollover states (e.g. 'base', 'over', 'down', 'off').
            if tokens[0] not in rollover_states:
                options = ', '.join(f"'{x}'" for x in rollover_states)
                raise ValueError(f"keyword argument '{key}' should begin with one of {options}")

            # If we just got the name of a state with no suffix, replace that 
            # state with the given argument (which should be a widget).
            if len(tokens) == 1:
                self._background.add_state(arg)

            # Otherwise, pass the argument through to the `set_appearance()` 
            # method for the indicated background widget.
            else:
                appearance_args[tokens[0]][tokens[1]] = arg

        # We have to make only one call to `set_appearance()` per background 
        # widget, otherwise later calls would override earlier calls.
        for key, args in appearance_args.items():
            self._background[key].set_appearance(**args)

    def del_background(self):
        self.set_background()

    def get_base_background(self):
        return self._background['base']

    def set_base_background(self, widget):
        self._background.add_state('base', widget)

    def get_over_background(self):
        return self._background['over']

    def set_over_background(self, widget):
        self._background.add_state('over', widget)

    def get_down_background(self):
        return self._background['down']

    def set_down_background(self, widget):
        self._background.add_state('down', widget)

    def get_off_background(self):
        return self._background['off']

    def set_off_background(self, widget):
        self._background.add_state('off', widget)

    def _yield_layers(self):
        if self._foreground:
            yield self._foreground
        yield self._background

    def _init_custom_background_appearances(self):
        """
        Setup the background widgets from parameters found in dynamically named
        `custom_...` class variables.

        For example, the class variable `custom_base_image = ...` would call 
        `set_appearance(image=...)` on the "base" background widget.
        """
        background_args = {}

        for key in self._background.known_states:
            background_args.update({
                    k[len('custom_'):]: v
                    for cls in self.__class__.__mro__
                    for k, v in cls.__dict__.items()
                    if k.startswith(f'custom_{key}_')
            })

        if background_args:
            self.set_background(**background_args)
            
@autoprop
@register_event_type('on_toggle')
class Checkbox(Widget):
    custom_checked_base = None; custom_unchecked_base = None
    custom_checked_over = None; custom_unchecked_over = None
    custom_checked_down = None; custom_unchecked_down = None
    custom_checked_off  = None; custom_unchecked_off  = None
    custom_alignment = 'center'

    def __init__(self, is_checked=False):
        super().__init__()
        self._deck = Deck(is_checked)
        self._attach_child(self._deck)
        self._defer_clicks_to_proxies = {}
        self.set_images(
                checked_base=self.custom_checked_base,
                checked_over=self.custom_checked_over,
                checked_down=self.custom_checked_down,
                checked_off=self.custom_checked_off,
                unchecked_base=self.custom_unchecked_base,
                unchecked_over=self.custom_unchecked_over,
                unchecked_down=self.custom_unchecked_down,
                unchecked_off=self.custom_unchecked_off,
        )

    def do_claim(self):
        return self._deck.claimed_size

    def on_click(self, widget):
        if self._defer_clicks_to_proxies and widget is self:
            return
        else:
            self.toggle()

    def toggle(self):
        if self.is_enabled:
            self._deck.state = not self._deck.state
            self.dispatch_event('on_toggle', self)

    def check(self):
        if not self.is_checked:
            self.toggle()

    def uncheck(self):
        if self.is_checked:
            self.toggle()

    @property
    def is_checked(self):
        return self._deck.state

    def set_images(self, *,
            checked_base=None, unchecked_base=None,
            checked_over=None, unchecked_over=None,
            checked_down=None, unchecked_down=None,
            checked_off=None,  unchecked_off=None):

        checked = Rollover(self, 'base')
        checked.add_states_if(
                lambda w: w.image is not None,
                base=Image(checked_base),
                over=Image(checked_over),
                down=Image(checked_down),
                off=Image(checked_off),
        )
        unchecked = Rollover(self, 'base')
        unchecked.add_states_if(
                lambda w: w.image is not None,
                base=Image(unchecked_base),
                over=Image(unchecked_over),
                down=Image(unchecked_down),
                off=Image(unchecked_off),
        )
        with self._deck.hold_updates():
            self._deck[True] = checked
            self._deck[False] = unchecked

    def del_images(self):
        self._deck.clear_states()

    def add_proxy(self, widget, exclusive=False):
        widget.push_handlers(on_click=self.on_click)
        widget.push_handlers(on_detach=self.remove_proxy)
        self._deck[True].add_controller(widget)
        self._deck[False].add_controller(widget)
        self._defer_clicks_to_proxies = exclusive

    def remove_proxy(self, widget, exclusive=False):
        widget.remove_handlers(on_click=self.on_click)
        widget.remove_handlers(on_detach=self.remove_proxy)
        self._deck[True].remove_controller(widget)
        self._deck[False].remove_controller(widget)
        self._defer_clicks_to_proxies = exclusive

@autoprop
class RadioButton(Checkbox):

    def __init__(self, peers=None, *, is_checked=False, **images):
        super().__init__(is_checked=is_checked, **images)
        self.peers = peers if peers is not None else []

    def on_toggle(self, widget):
        if self.is_checked:
            for peer in self.peers:
                if peer is not self:
                    peer.uncheck()

    def get_peers(self):
        return self._peers

    def set_peers(self, peers):
        if self not in peers:
            peers.append(self)
        self._peers = peers


