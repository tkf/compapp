from ..core import Descriptor

_type = type


def tupleoftypes(t):
    if isinstance(t, type):
        return (t,)
    assert isinstance(t, tuple)
    return t


class OfType(Descriptor):

    """
    Attribute accepting only certain type(s) of value.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     i = OfType(int)
    ...
    >>> MyParametric(i='a')
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.i only accepts type of int: got a

    `OfType` can take multiple classes:

    >>> class MyParametric(Parametric):
    ...     i = OfType(int, float, str)
    ...
    >>> mp = MyParametric()
    >>> mp.i = 'a'
    >>> mp.i = 1j
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.i only accepts type of int, float or str: got 1j

    It is an error to access unset an `OfType` attribute:

    >>> mp = MyParametric()
    >>> mp.i
    Traceback (most recent call last):
      ...
    AttributeError: 'MyParametric' object has no attribute 'i'

    `OfType` can take *default* argument:

    >>> class MyParametric(Parametric):
    ...     i = OfType(int, default=0)
    ...
    >>> mp = MyParametric()
    >>> mp.i
    0

    """

    def __init__(self, *classes, **kwds):
        super(OfType, self).__init__(**kwds)
        self.classes = classes

    def verify(self, obj, value, myname=None):
        if not isinstance(value, self.classes):
            if isinstance(self.classes, tuple):
                if len(self.classes) > 1:
                    classes = ', '.join(
                        cls.__name__ for cls in self.classes[:-1]
                    ) + ' or ' + self.classes[-1].__name__
                else:
                    classes = self.classes[0].__name__
            else:
                classes = self.classes.__name__
            raise ValueError(
                "{0}.{1} only accepts type of {2}: got {3}".format(
                    obj.__class__.__name__,
                    myname or self.myname(obj),
                    classes,
                    value))
        return value


class Required(Descriptor):

    """
    Attributes required to be set before `.Executable.run`.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     i = Required()
    ...
    >>> mp = MyParametric()
    >>> has_required_attributes(mp)
    False
    >>> mp.i = 1
    >>> has_required_attributes(mp)
    True

    >>> class MyParametric(Parametric):
    ...     i = Required(OfType(int))
    ...
    >>> mp = MyParametric()
    >>> has_required_attributes(mp)
    False
    >>> mp.i = '1'
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.i only accepts type of int: got 1
    >>> mp.i = 1
    >>> has_required_attributes(mp)
    True

    """

    def __init__(self, desc=None):
        super(Required, self).__init__()
        self.desc = desc
        if desc:
            # self.get = desc.get
            self.verify = desc.verify
            desc.myname = self.myname


def has_required_attributes(obj):  # FIXME call it via pre_run()
    for name in dir(obj.__class__):
        if not isinstance(getattr(obj.__class__, name), Required):
            continue
        if not hasattr(obj, name):
            return False
    return True


class List(Descriptor):

    """
    Attribute accepting only list with certain traits.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     anylist = List()
    ...     intlist = List(int)
    ...
    >>> mp = MyParametric()
    >>> mp.anylist = [1]
    >>> mp.anylist = ['a']
    >>> mp.intlist = [1]
    >>> mp.intlist = [0, 1, '2']
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.intlist[2] only accepts type of int: got 2

    """

    def __init__(self, trait=None, type=list, cast=None, **kwds):
        super(List, self).__init__(**kwds)
        self.type = self.allowed = tupleoftypes(type)
        if cast:
            cast = tupleoftypes(cast)
            self.allowed += cast
        self.cast = cast

        if isinstance(trait, (_type, tuple)):
            self.trait = OfType(*tupleoftypes(trait))
        else:
            assert isinstance(trait, (Descriptor, _type(None)))
            self.trait = trait

    def verify(self, obj, value):
        assert isinstance(value, self.allowed)
        if self.trait is None:
            return value
        myname = self.myname(obj)
        for i, x in enumerate(value):
            self.trait.verify(obj, x, myname='{0}[{1}]'.format(myname, i))
        return value
