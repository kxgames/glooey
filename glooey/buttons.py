#!/usr/bin/env python3

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
class Clickable(Widget):

    def __init__(self):
        super().__init__()
        self._last_rollover_event = 'base'
        self._mouse_state = 'base'
        self._active_state = True
        self._double_click_timer = 0

    def deactivate(self):
        self._active_state = False
        self._dispatch_rollover_event()

    def reactivate(self):
        self._active_state = True
        self._dispatch_rollover_event()

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        self._mouse_state = 'down'
        self._dispatch_rollover_event()

    def on_mouse_release(self, x, y, button, modifiers):
        import time
        super().on_mouse_release(x, y, button, modifiers)

        if self._active_state and self._mouse_state == 'down':
            self.dispatch_event('on_click', self)

            # Two clicks within 500 ms triggers a double-click.
            if time.perf_counter() - self._double_click_timer < 0.5:
                self.dispatch_event('on_double_click', self)
                self._double_click_timer = 0
            else:
                self._double_click_timer = time.perf_counter()

        self._mouse_state = 'over'
        self._dispatch_rollover_event()

    def on_mouse_enter(self, x, y):
        super().on_mouse_enter(x, y)
        self._mouse_state = 'over'
        self._dispatch_rollover_event()

    def on_mouse_leave(self, x, y):
        super().on_mouse_leave(x, y)
        self._mouse_state = 'base'
        self._dispatch_rollover_event()

    def on_mouse_drag_leave(self, x, y):
        super().on_mouse_drag_leave(x, y)
        self._mouse_state = 'base'
        self._dispatch_rollover_event()
    
    @property
    def is_active(self):
        return self._active_state

    def get_last_rollover_event(self):
        return self._last_rollover_event

    def _dispatch_rollover_event(self):
        rollover_event = self._mouse_state if self._active_state else 'off'
        if rollover_event != self._last_rollover_event:
            self.dispatch_event('on_rollover', rollover_event, self._last_rollover_event)
            self._last_rollover_event = rollover_event


Clickable.register_event_type('on_click')
Clickable.register_event_type('on_double_click')
Clickable.register_event_type('on_rollover')

@autoprop
class Rollover(Deck):
    custom_predicate = lambda self, w: True

    def __init__(self, clickable, initial_state, predicate=None, **widgets):
        super().__init__(initial_state, **widgets)
        self._predicate = predicate or self.custom_predicate
        clickable.push_handlers(self.on_rollover)

    def on_rollover(self, new_state, old_state):
        if self.is_state_missing(new_state) and new_state == 'down':
            new_state = 'over'

        if self.is_state_missing(new_state) and new_state == 'over':
            new_state = 'base'

        self.set_state(new_state)

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


@autoprop
class Button(Clickable):
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

    def __init__(self, text='', image=None):
        super().__init__()
        self._stack = Stack()
        self._label = self.Label()
        self._image = self.Image()
        self._backgrounds = {
                'base': self.Base(),
                'over': self.Over(),
                'down': self.Down(),
                'off': self.Off(),
        }
        self._rollover = Rollover(self, 'base', lambda w: not w.is_empty)
        self._rollover.add_states(**self._backgrounds)

        self.set_text(text)
        self.set_image(image)

        self._attach_child(self._stack)
        self._stack.insert(self._label, self.custom_label_layer)
        self._stack.insert(self._image, self.custom_image_layer)
        self._stack.insert(self._rollover, self.custom_background_layer)

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
class Checkbox(Clickable):
    custom_checked_base = None; custom_unchecked_base = None
    custom_checked_over = None; custom_unchecked_over = None
    custom_checked_down = None; custom_unchecked_down = None
    custom_checked_off  = None; custom_unchecked_off  = None
    custom_alignment = 'center'

    def __init__(self, is_checked=False):
        super().__init__()
        self._deck = Deck(is_checked)
        self._attach_child(self._deck)
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
        self.toggle()

    def toggle(self):
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
            self._deck.add_state(True, checked)
            self._deck.add_state(False, unchecked)

    def del_images(self):
        self._deck.clear_states()


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


