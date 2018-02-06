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
    Label = Label
    Image = Image
    Base = Background
    Over = Background
    Down = Background
    Off = Background

    custom_label_layer = 3
    custom_image_layer = 2
    custom_background_layer = 1
    custom_alignment = 'center'

    # These attributes are just provided for convenience.  They're redundant, 
    # strictly speaking, because they could also be set using inner classes.  
    custom_text = None
    custom_image = None

    def __init__(self, text=None, image=None):
        super().__init__()
        self._stack = Stack()
        self._label = self.Label(text or self.custom_text)
        self._image = self.Image(image or self.custom_image)
        self._backgrounds = {
                'base': self.Base(),
                'over': self.Over(),
                'down': self.Down(),
                'off': self.Off(),
        }
        self._rollover = Rollover(self, 'base', predicate=lambda w: not w.is_empty)
        self._rollover.add_states(**self._backgrounds)
        self._is_enabled = True

        self._attach_child(self._stack)
        self._stack.insert(self._label, self.custom_label_layer)
        self._stack.insert(self._image, self.custom_image_layer)
        self._stack.insert(self._rollover, self.custom_background_layer)

    def click(self):
        if self.is_enabled:
            self.dispatch_event('on_click')

    def do_claim(self):
        return self._stack.claimed_size

    def get_text(self):
        return self._label.text

    def set_text(self, text, **style):
        self._label.set_text(text, **style)

    def del_text(self):
        del self._label.text

    def get_label(self):
        return self._label

    def set_label(self, label, placement=None):
        self._stack.remove(self._label)
        self._label = label
        self._stack.insert(self._label, self.custom_label_layer)

    def get_image(self):
        return self._image.image

    def set_image(self, image):
        self._image.set_image(image)

    def del_image(self):
        del self._image.image

    def set_background(self, **kwargs):
        for state, widget in self._backgrounds.items():
            widget.set_appearance(**{
                k.split('_', 1)[1]: v
                for k,v in kwargs.items()
                if k.startswith(state)
            })

    def del_background(self):
        self.set_background()

    def get_base_background(self):
        return self._backgrounds['base']

    def get_over_background(self):
        return self._backgrounds['over']

    def get_base_background(self):
        return self._backgrounds['base']

    def get_off_background(self):
        return self._backgrounds['off']


@autoprop
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


Checkbox.register_event_type('on_toggle')

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


