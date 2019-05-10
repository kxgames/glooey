#!/usr/bin/env python3

"""
General-purpose utilities used throughout the project.
"""

import functools
import contextlib

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

    def pause_updates(self):
        self._num_holds += 1

    def resume_updates(self):
        self._num_holds = max(self._num_holds - 1, 0)
        if self._num_holds == 0:
            for update, args, kwargs in self._filter_pending_updates():
                update(self, *args, **kwargs)
            self._pending_updates = []

    def discard_updates(self):
        self._num_holds = max(self._num_holds - 1, 0)
        if self._num_holds == 0:
            self._pending_updates = []

    @contextlib.contextmanager
    def hold_updates(self):
        self.pause_updates()
        yield
        self.resume_updates()

    @contextlib.contextmanager
    def suppress_updates(self):
        self.pause_updates()
        yield
        self.discard_updates()

    def _filter_pending_updates(self):
        """
        Return all the updates that need to be applied, from a list of all the 
        updates that were called while the hold was active.  This method is 
        meant to be overridden by subclasses that want to customize how held 
        updates are applied.

        The `self._pending_updates` member variable is a list containing a 
        (method, args, kwargs) tuple for each update that was called while 
        updates were being held.  This list is in the order that the updates 
        were actually called, and any updates that were called more than once 
        will appear in this list more than once.
        
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


def register_event_type(*event_types):
    def decorator(cls):
        for event_type in event_types:
            cls.register_event_type(event_type)
        return cls
    return decorator
def late_binding_property(fget=None, fset=None, fdel=None, doc=None):
    import functools

    if fget is not None:
        def __get__(obj, objtype=None, name=fget.__name__):
            fget = getattr(obj, name)
            return fget()

        fget = functools.update_wrapper(__get__, fget)

    if fset is not None:
        def __set__(obj, value, name=fset.__name__):
            fset = getattr(obj, name)
            return fset(value)

        fset = functools.update_wrapper(__set__, fset)

    if fdel is not None:
        def __delete__(obj, name=fdel.__name__):
            fdel = getattr(obj, name)
            return fdel()

        fdel = functools.update_wrapper(__delete__, fdel)

    return property(fget, fset, fdel, doc)

def first_not_none(iterable):
    n = 0
    for x in iterable:
        if x is not None:
            return x
        n += 1

    raise ValueError("No values given." if n == 0 else f"All {n} values `None`.")

def clamp(value, low, high):
    return max(low, min(value, high))
