from contextlib import contextmanager
import itertools
import sys

PY3 = (sys.version_info[0] >= 3)


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


class MultiException(Exception):

    def __init__(self, message="Multiple exceptions are raised:",
                 errors=None):
        super(MultiException, self).__init__(message, errors)
        self.message = message
        self.errors = [] if errors is None else errors
        self.args = (message, self.errors)

    def __str__(self):
        msgs = map("* {0.__class__.__name__}: {0}".format, self.errors)
        return "\n".join(itertools.chain([self.message], msgs))

    def __fix_doc(f):
        # Workaround for Python 2/3 doctest difference.  I am doing
        # this in a decorator since it's not editable after
        # @classmethod.
        if not PY3:
            f.__doc__ = f.__doc__.replace('compapp.base.MultiException:',
                                          'MultiException:')
        return f

    @contextmanager
    def record(self, type=Exception):
        try:
            yield self
        except type as err:
            self.errors.append(err)

    @classmethod
    @contextmanager
    @__fix_doc
    def recorder(cls, *args, **kwds):
        """
        Context manager to raise error (if any) at the end of execution.

        >>> with MultiException.recorder() as mexc:
        ...     with mexc.record():
        ...         raise ValueError(1)
        ...     with mexc.record():
        ...         raise RuntimeError(2)
        Traceback (most recent call last):
          ...
        compapp.base.MultiException: Multiple exceptions are raised:
        * ValueError: 1
        * RuntimeError: 2

        """
        self = cls(*args, **kwds)
        yield self
        if self.errors:
            raise self

    @classmethod
    @__fix_doc
    def run(cls, callbacks, *args, **kwds):
        """
        Run all `callbacks` ignoring exceptions and raise at the end (if any).

        >>> def raiser(e):
        ...     raise e
        >>> MultiException.run([
        ...     # takes tuple (func, arg1, arg2, ...):
        ...     (raiser, ValueError(1)),
        ...     # or a function without any argument:
        ...     lambda: raiser(RuntimeError(2)),
        ... ])
        Traceback (most recent call last):
          ...
        compapp.base.MultiException: Multiple exceptions are raised:
        * ValueError: 1
        * RuntimeError: 2

        """
        pairs = ((c[0], c[1:]) if isinstance(c, tuple) else (c, ())
                 for c in callbacks)
        with cls.recorder() as mexc:
            for (f, args) in pairs:
                with mexc.record():
                    f(*args)


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
