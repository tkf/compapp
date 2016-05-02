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
    ...
    ...     class nest(Parametric):
    ...         x = 2
    ...         l0 = Link('')
    ...         l1 = Link('x')
    ...         l2 = Link('..x')
    ...         l3 = Link('.nest.x')
    ...
    ...         class nest(Parametric):
    ...             x = 3
    ...             l0 = Link('')
    ...             l1 = Link('x')
    ...             l2 = Link('..x')
    ...             l3 = Link('.nest.x')
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
