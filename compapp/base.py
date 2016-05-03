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
