#!/usr/bin/env python3

import functools
import contextlib
from pprint import pprint

class UsageError (Exception):
    pass

class NoParentError (UsageError):
    
    def __init__(self, widget):
        super().__init__("widget '{}' has not been attached to the GUI.".format(widget))



class HoldUpdatesMixin:

    def __init__(self, num_holds=0):
        super().__init__()
        self._num_holds = num_holds
        self._pending_updates = []

    def stop_updates(self):
        self._num_holds += 1

    def resume_updates(self):
        self._num_holds = max(self._num_holds - 1, 0)
        if self._num_holds == 0:
            for update, args, kwargs in self._filter_pending_updates():
                update(self, *args, **kwargs)
            self._pending_updates = []

    @contextlib.contextmanager
    def hold_updates(self):
        self.stop_updates()
        yield
        self.resume_updates()

    def _filter_pending_updates(self):
        """
        Return all the updates  that need to be applied, from a list of all the 
        updates that were called while the hold was active.  This method is 
        meant to be overridden by subclasses that want to customize how held 
        updates are applied.

        The self._pending_updates list contains a (method, args, kwargs) tuple 
        for each update that was called while updates were being held.  This 
        list is in the order that the updates were actually called, and any 
        updates that were called more than once will appear in this list more 
        than once.
        
        This method should yield or return an list of the tuples in the same 
        format representing the updates that should be applied, in the order 
        they should be applied.  The default implementation filters out 
        duplicate updates without changing their order.  In cases where it 
        matters, the last call to each update is used to determine the order.
        """
        from more_itertools import unique_everseen as unique
        yield from reversed(list(unique(reversed(self._pending_updates))))


def update_function(method):

    @functools.wraps(method)
    def wrapped_method(self, *args, **kwargs):
        if self._num_holds > 0:
            self._pending_updates.append((method, args, kwargs))
        else:
            method(self, *args, **kwargs)

    return wrapped_method



