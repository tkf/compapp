# FIXME: put the imports at the top-level; it cannot be done ATM since
# it makes imports circular.


def rec_setattr(obj, name, value):
    """
    Recursive version of `setattr`.

    If `value` is a `dict` *and* the attribute `name` of `obj` is some
    non-simple object, set attributes of it by the values of the
    dictionary `value`.  Otherwise fallbacks to `setattr`.

    """
    from .descriptors import Required, Optional
    if isinstance(value, dict):
        if isinstance(getattr(obj, name, None), dict):
            setattr(obj, name, value)
        elif isinstance(getattr(type(obj), name), (Required, Optional)):
            setattr(obj, name, value)
        else:
            rec_setattrs(getattr(obj, name), value)
    else:
        setattr(obj, name, value)


def rec_setattrs(obj, dct):
    """
    Set values of nested dictionary `dct` to attributes of `obj`.

    >>> class A(object):
    ...     b = c = d = e = f = None
    >>> a = A()
    >>> a.b = A()
    >>> a.b.c = A()
    >>> rec_setattrs(a, dict(b=dict(c=dict(d=1), e=2), f=3))
    >>> a.b.c.d
    1
    >>> a.b.e
    2
    >>> a.f
    3

    """
    from .descriptors import ClassPlaceholder
    namelist = list(dct)
    cls = type(obj)
    placeholders = {name for name in dir(cls) if
                    isinstance(getattr(cls, name), ClassPlaceholder)}
    for sublist in [set(namelist) - placeholders,
                    placeholders & set(namelist)]:
        for name in sublist:
            rec_setattr(obj, name, dct[name])
