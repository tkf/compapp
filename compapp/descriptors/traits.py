from ..core import Descriptor


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
    ValueError: MyParametric.i only accepts type of int: got 'a'

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
        self.allowed = classes

    @property
    def allowed(self):
        return self._allowed

    @allowed.setter
    def allowed(self, value):
        for t in value:
            assert isinstance(t, type)
        self._allowed = value

    def verify(self, obj, value, myname=None):
        if self.allowed and not isinstance(value, self.allowed):
            if isinstance(self.allowed, tuple):
                if len(self.allowed) > 1:
                    classes = ', '.join(
                        cls.__name__ for cls in self.allowed[:-1]
                    ) + ' or ' + self.allowed[-1].__name__
                else:
                    classes = self.allowed[0].__name__
            else:
                classes = self.allowed.__name__
            raise ValueError(
                "{0}.{1} only accepts type of {2}: got {3!r}".format(
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
    ValueError: MyParametric.i only accepts type of int: got '1'
    >>> mp.i = 1
    >>> has_required_attributes(mp)
    True

    """

    def __init__(self, desc=None):
        super(Required, self).__init__()
        if desc and not isinstance(desc, Descriptor):
            desc = OfType(desc)
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


def asdesc(trait):
    if isinstance(trait, (type, tuple)):
        return OfType(*tupleoftypes(trait))
    else:
        assert isinstance(trait, (Descriptor, type(None)))
        return trait


class List(OfType):

    """
    Attribute accepting only list with certain traits.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     anylist = List()
    ...     intlist = List(int)
    ...     castlist = List(int, cast=tuple)
    ...
    >>> mp = MyParametric()
    >>> mp.anylist = [1]
    >>> mp.anylist = ['a']
    >>> mp.intlist = [1]
    >>> mp.intlist = [0, 1, '2']
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.intlist[2] only accepts type of int: got '2'

    >>> mp.intlist = (1,)
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.intlist only accepts type of list: got (1,)
    >>> mp.castlist = (1,)
    >>> mp.castlist
    [1]

    """

    def __init__(self, trait=None, type=list, cast=None, **kwds):
        allowed = (type,)
        if cast:
            cast = tupleoftypes(cast)
            allowed += cast

        super(List, self).__init__(*allowed, **kwds)

        self.type = type
        self.cast = cast
        self.trait = asdesc(trait)

    def verify(self, obj, value, myname=None):
        super(List, self).verify(obj, value, myname=myname)
        if not isinstance(value, self.type):
            value = self.type(value)

        if self.trait is None:
            return value
        myname = myname or self.myname(obj)
        for i, x in enumerate(value):
            self.trait.verify(obj, x, myname='{0}[{1}]'.format(myname, i))
        return value


class Dict(OfType):

    """
    Attribute accepting only dict with certain traits.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     anydict = Dict()
    ...     strint = Dict(str, int)
    ...
    >>> mp = MyParametric()
    >>> mp.anydict = {'a': 1}
    >>> mp.strint = {'a': 1}
    >>> mp.strint = {1: 1}
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.strint[...] only accepts type of str: got 1
    >>> mp.strint = {'a': 'b'}
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.strint['a'] only accepts type of int: got 'b'

    """

    def __init__(self, key=None, value=None, type=dict, cast=None,
                 **kwds):
        allowed = (type,)
        if cast:
            cast = tupleoftypes(cast)
            allowed += cast

        super(Dict, self).__init__(**kwds)

        self.type = type
        self.cast = cast
        self.keytrait = asdesc(key)
        self.valuetrait = asdesc(value)

    def verify(self, obj, value, myname=None):
        super(Dict, self).verify(obj, value, myname=myname)
        if not isinstance(value, self.type):
            value = self.type(value)

        myname = myname or self.myname(obj)
        if self.keytrait:
            for k in value:
                self.keytrait.verify(obj, k, myname='{0}[...]'.format(myname))
        if self.valuetrait:
            for k, v in value.items():
                self.valuetrait.verify(obj, v,
                                       myname='{0}[{1!r}]'.format(myname, k))
        return value


class Choice(Descriptor):

    """
    Attribute accepting only one of the specified value.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     choice = Choice(1, 2, 'a')
    ...
    >>> mp = MyParametric()
    >>> mp.choice = 1
    >>> mp.choice = 'a'
    >>> mp.choice = 'unknown'              # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.choice only accepts one of (1, 2, 'a'):
    got 'unknown'

    """

    def __init__(self, *choices, **kwds):
        super(Choice, self).__init__(*kwds)
        self.choices = choices

    def verify(self, obj, value, myname=None):
        if value not in self.choices:
            raise ValueError(
                "{0}.{1} only accepts one of {2}: got {3!r}".format(
                    obj.__class__.__name__,
                    myname or self.myname(obj),
                    self.choices,
                    value))
        return value


class Or(Descriptor):

    """
    Use one of the specified traits.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     attr = Or(Choice(*'abc'), OfType(int))
    ...
    >>> mp = MyParametric()
    >>> mp.attr = 'a'
    >>> mp.attr = 1
    >>> mp.attr = 1.0
    Traceback (most recent call last):
      ...
    ValueError: None of the traits are matched to: 1.0

    .. todo:: `Or` should work with link-type descriptor.

    """

    def __init__(self, *traits, **kwds):
        super(Or, self).__init__(**kwds)
        self.traits = traits

    def verify(self, obj, value, myname=None):
        myname = myname or self.myname(obj)
        for trait in self.traits:
            try:
                trait.verify(obj, value, myname=myname)
                return value
            except ValueError:
                continue
        raise ValueError("None of the traits are matched to: {0!r}"
                         .format(value))
