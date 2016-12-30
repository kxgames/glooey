#!/usr/bin/env python3

import inspect
import functools
import contextlib
from pprint import pprint

class UsageError (Exception):
    pass

class NoParentError (UsageError):
    
    def __init__(self, widget):
        super().__init__("widget '{}' has not been attached to the GUI.".format(widget))



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


class HoldUpdatesMixin:

    def __init__(self):
        super().__init__()
        self._hold_updates = False
        self._update_order = {}
        self._stale_update_functions = set()

        for name, method in inspect.getmembers(self):
            try: self._update_order[name] = method._hold_updates_exe_order
            except AttributeError: pass

    @contextlib.contextmanager
    def hold_updates(self):
        self._hold_updates = True
        self._stale_update_functions = set()

        yield

        self._hold_updates = False
        for name in sorted(self._stale_update_functions,
                key=lambda x: self._update_order[x]):
            getattr(self, name)()
        self._stale_update_functions = set()


class update_function:

    def __init__(self, exe_order):
        if not isinstance(exe_order, int):
            raise ValueError(f"Execution order must be an integer, not {exe_order}")
        self.exe_order = exe_order

    def __call__(self, method):
        args = inspect.getfullargspec(method)
        if len(args.args) - 1 > len(args.defaults or ()):
            raise TypeError("update functions can't take any arguments (besides self).")

        @functools.wraps(method)
        def wrapped_method(self, *args, **kwargs):
            if self._hold_updates:
                self._stale_update_functions.add(method.__name__)
            else:
                method(self, *args, **kwargs)

        wrapped_method._hold_updates_exe_order = self.exe_order
        return wrapped_method


