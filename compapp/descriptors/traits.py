from ..core import Descriptor


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

    def verify(self, obj, value):
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
                    self.myname(obj),
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
