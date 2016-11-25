#!/usr/bin/env python3

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

