from .core import Parameter


class Link(Parameter):

    """
    "Link" parameter.

    It's like symbolic-link in the file system.

    Examples
    --------

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

    def __init__(self, path):
        self.path = path


class Root(Link):

    """
    An alias of ``Link('')``.
    """

    def __init__(self):
        super(Root, self).__init__('')


class Delegate(Parameter):

    """
    Delegate parameter to its owner.

    ``x = Delegate('x')`` is an shortcut of ``x = Link('..x')``.

    Examples
    --------

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


class Owner(Parameter):

    """
    Link to its owner.

    Examples
    --------
    >>> class MyParametric(Parametric):
    ...     class nest(Parametric):
    ...         owner = Owner()
    ...
    >>> par = MyParametric()
    >>> par is par.nest.owner
    True

    """


class OwnerInfo(Parameter):

    """
    Refer to information of owner.

    Examples
    --------
    >>> class MyDelegate(Link):
    ...
    ...     ownerinfo = OwnerInfo()
    ...
    ...     def __init__(self):
    ...         super(MyDelegate, self).__init__(self.ownerinfo.name)

    """

    @property
    def name(self):
        """
        Name of the owner.
        """

    @property
    def value(self):
        """
        The owner itself.
        """


class Propagate(Parameter):

    r"""
    Propagate value to nested classes.

    >>> class Parent(Parametric):
    ...
    ...     class nest1(Parametric):
    ...         sampling_period = 0.0
    ...
    ...     class nest2(Parametric):
    ...         sampling_period = 0.0
    ...
    ...     sampling_period = Propagate(10.0)
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

    Note that it is not equivalent to having `Delegate` for
    nested classes.  Changing parameter in nested does not
    "propagate back" to its owner classes.

    >>> par.nest1.sampling_period = 30.0
    >>> par.sampling_period
    10.0

    .. todo:: Clarify this point.  Isn't it the same for `Delegate`?
       Maybe `Delegate`\ ed attribute should be un-settable (hence
       making a difference)?

    """
# TODO: Is it fine to have BOTH `Delegate` and `Propagate`?  Are they
# any situation these two interfere in a complicated way?


class Instance(Parameter):

    """
    Check if the property is of a specific type.
    """

    def __init__(self, type):
        pass


class Required(Parameter):

    """
    """

    def __init__(self, type=None):
        pass


class Optional(Parameter):

    """
    Optional parameter.

    Examples
    --------
    >>> class MyParametric(Parametric):
    ...     i = Optional(int)
    ...     j = Optional(int)
    >>> MyParametric.get_param_names()
    []
    >>> MyParametric().get_params()
    {}
    >>> MyParametric(i=1).get_params()
    {'i': 1}

    This is useful when writing `Parametric` interface to external
    library because you would like to avoid writing all default
    parameters in this case.  A simple interface to
    `matplotlib.pyplot.hist` can be written as:

    >>> class Hist(Parametric):
    ...
    ...     bins = Optional(int)
    ...     range = Optional()
    ...     normed = Optional(bool)
    ...
    ...     def plot(self, ax, x):
    ...         ax.hist(x, **self.get_params())

    """


class List(Parameter):

    """
    """


class Dict(Parameter):

    """
    """


class CSVList(Parameter):
    """
    """

    def __init__(self, value=None, type=str, len=None):
        self.type = type
        self.len = len
        self.default = value


class Choice(Parameter):
    """
    """


class Or(Parameter):
    """
    """


class LiteralEval(Parameter):
    """
    """
