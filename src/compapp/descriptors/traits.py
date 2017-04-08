import copy
import functools

from ..base import Unspecified
from ..core import cast_map, private, DataDescriptor
from ..parser import parse_bool


def tupleoftypes(t):
    if isinstance(t, type):
        return (t,)
    assert isinstance(t, tuple)
    return t


def skip_non_str(func):
    @functools.wraps(func)
    def wrapper(self, value):
        if not isinstance(value, str):
            return value
        return func(self, value)
    return wrapper


class OfType(DataDescriptor):

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
    ValueError: MyParametric.i only accepts type of int: got 'a' of type str

    `OfType` can take multiple classes:

    >>> class MyParametric(Parametric):
    ...     i = OfType(int, float, str)
    ...
    >>> mp = MyParametric()
    >>> mp.i = 'a'
    >>> mp.i = 1j                          # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.i only accepts type of int, float or str: got 1j
    of type complex

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

    Castable values are cast automatically:

    >>> class MyParametric(Parametric):
    ...     x = OfType(float)
    ...
    >>> mp = MyParametric()
    >>> mp.x = 1                          # assigning an int...
    >>> assert isinstance(mp.x, float)    # ... cast to a float
    >>> import numpy
    >>> mp.x = numpy.float16(2.0)         # assigning a numpy float...
    >>> assert isinstance(mp.x, float)    # ... cast to a float

    """

    def __init__(self, *classes, **kwds):
        init = kwds.pop('init', None)
        super(OfType, self).__init__(**kwds)
        if isinstance(init, type) and init not in classes:
            classes = (init,) + classes
        self.init = init
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
        for t in self.allowed:
            if isinstance(value, t):
                return value
            if t in cast_map and isinstance(value, cast_map[t]):
                return t(value)
        if self.allowed:
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
                "{0}.{1} only accepts type of {2}: got {3!r} of type {4}"
                .format(
                    obj.__class__.__name__,
                    myname or self.myname(obj),
                    classes,
                    value,
                    type(value).__name__,
                ))
        return value

    def get(self, obj):
        got = super(OfType, self).get(obj)
        if got is Unspecified and self.init is not None:
            got = self.init()
            self.__set__(obj, got)
        if got is not Unspecified and got is self.default:
            got = copy.deepcopy(got)
            self.__set__(obj, got)
        return got

    @skip_non_str
    def parse(self, string):
        for cls in self.allowed:
            try:
                if cls is bool:
                    val = parse_bool(string)
                    if isinstance(val, bool):
                        return val
                    continue
                return cls(string)
            except ValueError:
                pass
        raise ValueError("{0} cannot parse {1!r}".format(self.allowed, string))


class Required(DataDescriptor):

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
    ValueError: MyParametric.i only accepts type of int: got '1' of type str
    >>> mp.i = 1
    >>> has_required_attributes(mp)
    True

    """

    def __init__(self, desc=None):
        super(Required, self).__init__()
        if desc and not isinstance(desc, DataDescriptor):
            desc = OfType(desc)
        self.desc = desc
        if desc:
            # self.get = desc.get
            self.verify = desc.verify
            self.parse = desc.parse
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
        assert isinstance(trait, (DataDescriptor, type(None)))
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
    >>> mp.intlist = [0, 1, '2']            # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.intlist[2] only accepts type of int: got '2'
    of type str

    >>> mp.intlist = (1,)                  # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.intlist only accepts type of list: got (1,)
    of type tuple
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
    >>> mp.strint = {1: 1}                 # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.strint[...] only accepts type of str: got 1
    of type int
    >>> mp.strint = {'a': 'b'}             # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.strint['a'] only accepts type of int: got 'b'
    of type str

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


class Optional(OfType):

    """
    Optional parameter.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     i = Optional(int)
    ...     j = Optional(int)
    >>> sorted(MyParametric.paramnames())
    ['i', 'j']
    >>> MyParametric().params()
    {}
    >>> MyParametric(i=1).params()
    {'i': 1}
    >>> MyParametric(j=2).params()
    {'j': 2}
    >>> assert MyParametric(i=1, j=2).params() == {'i': 1, 'j': 2}
    >>> MyParametric(i='alpha')            # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.i only accepts type of int: got 'alpha'
    of type str

    This is useful when writing `Parametric` interface to external
    library because you would like to avoid writing all default
    parameters in this case.  A simple interface to
    `matplotlib.pyplot.hist` can be written as:

    >>> class Hist(Parametric):
    ...
    ...     bins = Optional(int)
    ...     normed = Optional(bool)
    ...
    ...     def plot(self, ax, x):
    ...         ax.hist(x, **self.params())
    ...
    >>> from matplotlib import pyplot
    >>> fig, ax = pyplot.subplots()
    >>> Hist(bins=100, normed=True).plot(ax, range(100))
    >>> pyplot.close(fig)

    """

    def verify(self, obj, value, myname=None):
        ret = super(Optional, self).verify(obj, value, myname)
        private(obj).optparams.append(self.myname(obj, error=True))
        return ret


class Choice(DataDescriptor):

    """
    Attribute accepting only one of the specified value.

    Parameters
    ----------
    default
        Default value (see *nodefault*).
    *choices
        Alternative values.
    nodefault : bool
        Treat *default* is just an alternative; i.e., do not
        "initialize" the attribute.
    **kwds
        See: `.DataDescriptor`.

    Examples
    --------

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     choice = Choice(1, 2, 'a')
    ...
    >>> mp = MyParametric()
    >>> mp.choice
    1
    >>> mp.choice = 2
    >>> mp.choice = 'a'
    >>> mp.choice = 'unknown'              # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: MyParametric.choice only accepts one of (1, 2, 'a'):
    got 'unknown'

    """

    def __init__(self, default, *choices, **kwds):
        if not kwds.pop('nodefault', False):
            kwds.update(default=default)
        super(Choice, self).__init__(**kwds)
        self.choices = (default,) + choices

    def verify(self, obj, value, myname=None):
        if value not in self.choices:
            raise ValueError(
                "{0}.{1} only accepts one of {2}: got {3!r}".format(
                    obj.__class__.__name__,
                    myname or self.myname(obj),
                    self.choices,
                    value))
        return value

    @skip_non_str
    def parse(self, string):
        for choice in self.choices:
            if isinstance(choice, str):
                val = string
            elif isinstance(choice, bool):
                val = parse_bool(string)
            else:
                try:
                    val = type(choice)(string)
                except ValueError:
                    continue
            if val == choice:
                return choice
        raise ValueError("{0} cannot parse {1!r}".format(self, string))


class Or(DataDescriptor):

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

    `Or` can be combined with `.Link`-like descriptors:

    >>> from compapp.descriptors import Delegate
    >>> class MyRoot(Parametric):
    ...     attr = Choice(*'abc', nodefault=True)
    ...
    ...     class nested(Parametric):
    ...         attr = Or(OfType(int), Delegate())
    ...
    >>> par = MyRoot()
    >>> par.nested.attr
    Traceback (most recent call last):
      ...
    AttributeError: 'nested' object has no attribute 'attr'

    If ``par.nested.attr`` is not specified (i.e., ``OfType(int)`` is
    not in action), accessing to ``par.nested.attr`` invokes
    `.Delegate` which tries to access ``par.attr``.  In the above
    example, ``par.attr`` was not set so the `AttributeError` was
    raised.  Setting ``par.attr`` makes ``par.nested.attr``
    accessible:

    >>> par.attr = 'b'
    >>> par.nested.attr
    'b'

    Specifying ``par.nested.attr`` directly invokes `.OfType`:

    >>> par.nested.attr = 'c'
    Traceback (most recent call last):
      ...
    ValueError: None of the traits are matched to: 'c'
    >>> par.nested.attr = 496
    >>> par.nested.attr
    496

    """

    def __init__(self, *traits, **kwds):
        self.traits = traits  # has to come before __init__ (see key.setter)
        super(Or, self).__init__(**kwds)
        self.myname = self.myname  # FIXME: an awful hack

    # The value of `.key` and `.myname` are propagated to the
    # component traits (`.traits`).  To allow nested Or trait, it is
    # done in the setter descriptor.

    # Propagation of self.myname in __init__ is an awful hack.  I need
    # to fix interface (use of myname, etc.) at some point.  But it
    # works for now...

    # Here is how it works: key.setter (and also myname.setter) is
    # called in two ways.  (1) The setter is called in __init__().
    # This time, it is set to the default implementation
    # "Descriptor.key()".  (2) The setter is called from the setter of
    # parent descriptor (i.e., via Or.__init__() of the parent).  The
    # outmost Or descriptor only hits the case (1).  All inner Or
    # descriptors are hit by the case (2) recursively.  This way, key
    # is propagated to all inner descriptors.

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value
        for trait in self.traits:
            trait.key = value

    def _myname(self, *args, **kwds):
        return super(Or, self).myname(*args, **kwds)

    @property
    def myname(self):
        return self._myname

    @myname.setter
    def myname(self, value):
        self._myname = value
        for trait in self.traits:
            trait.myname = value

    def verify(self, obj, value, myname=None):
        myname = myname or self.myname(obj)
        for trait in self.traits:
            try:
                verify = trait.verify
            except AttributeError:
                continue
            try:
                verify(obj, value, myname=myname)
                return value
            except ValueError:
                continue
        raise ValueError("None of the traits are matched to: {0!r}"
                         .format(value))

    def get(self, obj):
        for trait in self.traits:
            got = trait.get(obj)
            if got is not Unspecified:
                return got
        return self.default

    @skip_non_str
    def parse(self, string):
        for trait in self.traits:
            try:
                parse = trait.parse
            except AttributeError:
                continue
            try:
                return parse(string)
            except ValueError:
                continue
        raise ValueError("{0} cannot parse {1!r}".format(self.traits, string))

    @property
    def default(self):
        default = getattr(self, '_default', Unspecified)
        if default is not Unspecified:
            return default
        for trait in self.traits:
            if trait.default is not Unspecified:
                return trait.default
        return Unspecified

    @default.setter
    def default(self, value):
        self._default = value
