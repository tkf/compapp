from ..core import private, Descriptor


def countprefix(string, prefix):
    w = len(prefix)
    n = len(string)
    i = 1
    while i < n and string[i * w: (i+1) * w] == prefix:
        i += 1
    return i


class Link(Descriptor):

    """
    "Link" parameter.

    It's like symbolic-link in the file system.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     x = 1
    ...     broken = Link('..')
    ...
    ...     class nest(Parametric):
    ...         x = 2
    ...         l0 = Link('')
    ...         l1 = Link('x')
    ...         l2 = Link('..x')
    ...         l3 = Link('.nest.x')
    ...         broken = Link('..broken')
    ...
    ...         class nest(Parametric):
    ...             x = 3
    ...             l0 = Link('')
    ...             l1 = Link('x')
    ...             l2 = Link('..x')
    ...             l3 = Link('.nest.x')
    ...             broken = Link('..broken')
    ...
    >>> par = MyParametric()
    >>> par is par.nest.l0 is par.nest.nest.l0
    True
    >>> par.nest.l1
    1
    >>> par.nest.l2
    1
    >>> par.nest.l3
    3
    >>> par.nest.nest.l1
    1
    >>> par.nest.nest.l2
    2
    >>> par.nest.nest.l3
    Traceback (most recent call last):
      ...
    AttributeError: 'nest' object has no attribute 'l3'
    >>> hasattr(par, 'broken')
    False
    >>> hasattr(par.nest, 'broken')
    False
    >>> hasattr(par.nest.nest, 'broken')
    False


    .. todo:: Should `path` use more explicit notation as in the JSON
       pointer?  That is to say, use ``'#'`` instead of ``''`` (an
       empty string) to indicate the root.  Then, for example, ``'x'``
       would be written as ``'#.x'``.

    """

    def __init__(self, path, adapter=None, **kwds):
        super(Link, self).__init__(**kwds)
        self.path = path
        self.adapter = adapter

    def get(self, obj):
        if self.path.startswith('.'):
            i = countprefix(self.path, '.')
            start = obj
            for _ in range(i - 1):
                start = private(start).owner
                if start is None:
                    return self.default
            restpath = self.path[i:]
        else:
            restpath = self.path
            start = private(obj).getroot()

        value = start
        for part in restpath.split('.') if restpath else []:
            try:
                value = getattr(value, part)
            except AttributeError:
                return self.default

        if self.adapter:
            value = self.adapter(value)

        return value


class Root(Link):

    """
    An alias of ``Link('')``.
    """

    def __init__(self, **kwds):
        super(Root, self).__init__('', **kwds)


class Delegate(Link):

    """
    Delegate parameter to its owner.

    ``x = Delegate()`` is equivalent to ``x = Link('..x')``.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class Parent(Parametric):
    ...
    ...     class nest1(Parametric):
    ...         sampling_period = Delegate()
    ...
    ...     class nest2(Parametric):
    ...         sampling_period = Delegate()
    ...
    ...     sampling_period = 10.0
    ...
    >>> par = Parent()
    >>> par.sampling_period
    10.0
    >>> par.nest1.sampling_period
    10.0
    >>> par.nest2.sampling_period
    10.0
    >>> par.sampling_period = 20.0
    >>> par.nest1.sampling_period
    20.0

    """

    def __init__(self, **kwds):
        super(Delegate, self).__init__(None, **kwds)

    def get(self, obj):
        # FIXME: This is a bit hacky implementation (communicating by
        # mutating shared namespace).  Need refactoring.
        self.path = '..' + self.myname(obj)
        return super(Delegate, self).get(obj)


class MyName(Descriptor):
    def get(self, obj):
        return private(obj).myname


class OwnerName(Descriptor):
    def get(self, obj):
        return private(private(obj).owner).myname
