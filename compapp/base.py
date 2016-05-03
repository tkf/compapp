def constant(cls):
    """
    Pickleable singleton generator.
    """
    cls.__repr__ = cls.__reduce__ = lambda self: self.__class__.__name__
    return cls()


@constant
class Unspecified(object):
    """
    A placeholder singleton to indicate that the argument is not specified.
    """


class DictObject(object):

    """
    Dict-Object Hybrid

    Example
    -------

    >>> obj = DictObject()
    >>> obj['mykey'] = 'myval'
    >>> obj.mykey
    'myval'
    >>> obj()
    {'mykey': 'myval'}
    >>> obj
    DictObject({'mykey': 'myval'})
    >>> 'mykey' in obj
    True
    >>> '__init__' in obj
    False
    >>> list(obj)
    ['mykey']
    >>> len(obj)
    1
    >>> del obj['mykey']
    >>> len(obj)
    0
    >>> obj.mykey = 'anotherval'
    >>> obj['mykey']
    'anotherval'
    >>> del obj.mykey
    >>> len(obj)
    0
    >>> obj = DictObject()
    >>> obj
    DictObject({})

    """

    def __init__(self, *args, **kwds):
        self.__dict__.update(*args, **kwds)

    def __getitem__(self, name):
        return self.__dict__[name]

    def __setitem__(self, name, value):
        self.__dict__[name] = value

    def __call__(self):
        return self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __delitem__(self, x):
        del self.__dict__[x]

    def __contains__(self, x):
        return x in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self.__dict__)


def nesteditems(dct, emptydict=False):
    """
    Works like `dict.iteritems` but iterate over all descendant items.

    >>> dct = dict(a=1, b=2, c=dict(d=3, e=4))
    >>> sorted(nesteditems(dct))
    [(('a',), 1), (('b',), 2), (('c', 'd'), 3), (('c', 'e'), 4)]

    If "leaf" dict is empty, keys will not be yielded.

    >>> sorted(nesteditems(dict(a={}, b=dict(c={}))))
    []

    If ``emptydict=True``, empty dictionary is regarded as a value so
    that items with empty dict as value are yielded.

    >>> sorted(nesteditems(dict(a={}, b=dict(c={})), emptydict=True))
    [(('a',), {}), (('b', 'c'), {})]

    """
    for (key0, val0) in dct.items():
        if isinstance(val0, dict) and (not emptydict or val0):
            for (key, val) in nesteditems(val0, emptydict=emptydict):
                yield ((key0,) + key, val)
        else:
            yield ((key0,), val0)


def setnestedattr(obj, dct, emptydict=False):
    """
    Set values of nested dictionary `dct` to attributes of `obj`.

    >>> class A(object):
    ...     pass
    >>> a = A()
    >>> a.b = A()
    >>> a.b.c = A()
    >>> setnestedattr(a, dict(b=dict(c=dict(d=1), e=2), f=3))
    >>> a.b.c.d
    1
    >>> a.b.e
    2
    >>> a.f
    3

    """
    for keys, val in nesteditems(dct, emptydict=emptydict):
        holder = obj
        for k in keys[:-1]:
            holder = getattr(holder, k)
        setattr(holder, keys[-1], val)
