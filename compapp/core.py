from __future__ import print_function

import itertools
import logging


logger = logging.getLogger(__name__)


class Parameter(object):
    pass


simple_types = (
    complex,
    float,
    int,
    str,
    bool,
)
try:
    simple_types += (long, unicode)
except NameError:
    pass

basic_types = simple_types + (tuple, list, dict, set)
"""
Basic Python types.
"""

cast_map = {}
cast_map[float] = (int,)
cast_map[complex] = (int, float)
try:
    cast_map[float] += (long,)
    cast_map[long] = (int,)
    cast_map[unicode] = (str,)
except NameError:
    pass

_type = type


def simple_type_check(default, actual, errfmt, **fmtkwds):
    defaulttype = type(default)
    castables = (defaulttype,) + cast_map.get(defaulttype, ())
    if isinstance(actual, castables):
        return defaulttype(actual)
    castablenames = ', '.join(c.__name__ for c in castables)
    kwds = dict(fmtkwds, actualtype=type(actual), **locals())
    raise ValueError(errfmt.format(**kwds))


def itervars(obj):
    for name in dir(obj):
        if name.startswith('_'):
            continue
        yield name, getattr(obj, name)


def attrs_of(obj, type):
    for _, val in itervars(obj):
        if isinstance(val, type):
            yield val


def mixdicts(dicts):
    mixed = {}
    for d in dicts:
        mixed.update(d)
    return mixed


def automixin(owner, key, params):
    defaults = []
    for cls in owner.mro():
        try:
            nested = getattr(cls, key)
        except AttributeError:
            continue
        if issubclass(nested, Parametric):
            return nested(*defaults[::-1], **params)
        defaults.append(itervars(nested))


def _is_mixable_3(cls):
    return isinstance(cls, type) and (
        issubclass(cls, Parametric) or len(cls.mro()) == 2
    )

try:
    from types import ClassType

    def _is_mixable(cls):
        return _is_mixable_3(cls) or type(cls) == ClassType
except ImportError:
    _is_mixable = _is_mixable_3


class Descriptor(object):

    def __init__(self, default):
        self.default = default


class Parametric(Parameter):

    """
    The basic parametrized class.

    Any properties which are a subclass of `Parameter` or whose type
    are one of `basic_types` are considered as "parameter" to the
    class.

    Note that `Parametric` class itself is a subclass of `Parameter`.
    Thus, it allows "nested parameter", i.e., `Parametric` class
    having `Parametric` property.

    Example
    -------

    >>> class MyParametric(Parametric):
    ...     i = 1
    ...     x = 2.0
    ...
    ...     class param(Parametric):
    ...         a = 100
    ...         b = 200
    ...
    >>> mp = MyParametric({'i': 30, 'param': {'a': 0}})
    >>> mp.x
    2.0
    >>> mp.i
    30
    >>> mp.param.a
    0
    >>> mp.param.b
    200

    **Automatic parameter mix-in.**
    If it is just for resetting parameter, you don't need to inherit
    nested `Parametric` classes; it happens automatically.

    >>> class Base(Parametric):
    ...     class x(Parametric):
    ...         i = 0
    ...         j = 1
    ...
    >>> class Another(Base):
    ...     class x:  # do not need to inherit Base.x
    ...         i = -1
    ...
    >>> par = Another()
    >>> par.x.i
    -1
    >>> par.x.j
    1

    **Automatic type-checking and casting.**

    >>> MyParametric(i='a')     # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Traceback (most recent call last):
      ...
    ValueError: Value 'a' (type: str) cannot be assigned to the
    variable MyParametric.i (default: 1) ...
    >>> mp = MyParametric()
    >>> mp.x = 1j               # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    Traceback (most recent call last):
      ...
    ValueError: Value 1j (type: complex) cannot be assigned to the
    variable MyParametric.x (default: 2.0) ...
    >>> MyParametric(x=10).x
    10.0

    """

    def __init__(self, *args, **kwds):
        params = mixdicts(args + (kwds,))
        nestedparams = {}
        for (key, val) in params.items():
            default = getattr(self.__class__, key, None)
            if _is_mixable(default):
                nestedparams[key] = val
            else:
                setattr(self, key, val)

        for key, cls in itervars(self.__class__):
            if not _is_mixable(cls):
                continue

            val = automixin(self.__class__, key, nestedparams.get(key, {}))
            if val is not None:
                setattr(self, key, val)
                continue

            # If `automixin` return `None` it means that none of the
            # super classes of self don't have a Parametric subclass
            # as its attribute of the same name `key`.  Thus,
            # self.<key> holds some non-parameter value and setting it
            # is an error:

            if key in nestedparams:
                raise ValueError('Setting non-Parametric property {0}'
                                 .format(key))

    def __setattr__(self, name, value):
        default = getattr(self.__class__, name, None)
        if isinstance(default, simple_types):
            value = simple_type_check(
                default, value,
                "Value {actual!r} (type: {actualtype.__name__})"
                " cannot be assigned to the variable"
                " {self.__class__.__name__}.{name}"
                " (default: {default}) which only accepts one of"
                " the following types: {castablenames}.",
                name=name, self=self)
        super(Parametric, self).__setattr__(name, value)

    def params(self, nested=False, type=None):
        """
        Get parameters as a `dict`.

        Parameters
        ----------
        nested : bool
            if true, return a nested `dict` for `Parametric`
            properties.
        type
            type of parameters to be returned

        Returns
        -------
        params : dict

        Example
        -------
        >>> class MyParametric(Parametric):
        ...     x = 1.0
        ...     i = 1
        ...     s = 'A'
        ...
        ...     class ps(Parametric):
        ...         y = 2.0
        ...         j = 2
        ...
        >>> mp = MyParametric()
        >>> mp.params() == {'x': 1.0, 'i': 1, 's': 'A'}
        True
        >>> mp.params(nested=True) == dict(mp.params(), ps=dict(y=2.0, j=2))
        True
        >>> mp.params(nested=True, type=int) == {'i': 1, 'ps': {'j': 2}}
        True

        """
        if type is None:
            nametypes = None
        else:
            if not isinstance(type, tuple):
                type = (type,)
            nametypes = type + (Parametric,)

        params = {}
        for name in self.paramnames(type=nametypes):
            val = getattr(self, name)
            if isinstance(val, Parametric):
                if nested:
                    params[name] = val.params(nested=nested, type=type)
            else:
                params[name] = val
        return params

    @classmethod
    def paramnames(cls, type=None):
        """
        List names of parameter for this class.

        User sub-class can modify own behavior by overriding this
        method.

        Example
        -------
        >>> class MyParametric(Parametric):
        ...     x = 1.0
        ...     i = 1
        ...     s = 'string'
        ...
        ...     class ps(Parametric):
        ...         pass
        ...
        >>> sorted(MyParametric.paramnames())
        ['i', 'ps', 's', 'x']
        >>> MyParametric.paramnames(type=float)
        ['x']

        """
        # FIXME: optimize!
        names = list(cls.defaultparams(type=type))
        for name, val in itervars(cls):
            if isinstance(val, _type) and issubclass(val, Parametric):
                if type is None or issubclass(val, type):
                    names.append(name)
        return names

    @classmethod
    def defaultparams(cls, nested=False, type=None):
        r"""
        Get default parameters as a `dict`.

        Example
        -------
        >>> class MyParametric(Parametric):
        ...     x = 1.0
        ...     i = 1
        ...     s = 'string'
        ...
        ...     class ps(Parametric):
        ...         y = 2.0
        ...         j = 2
        ...
        >>> shallow = {
        ...     'x': 1.0, 'i': 1, 's': 'string'
        ... }
        >>> MyParametric.defaultparams() == shallow
        True
        >>> MyParametric.defaultparams(nested=True) \
        ...     == dict(shallow, ps={'y': 2.0, 'j': 2})
        True
        >>> MyParametric.defaultparams(nested=True, type=int) \
        ...     == {'i': 1, 'ps': {'j': 2}}
        True

        """
        params = {}
        for name, val in itervars(cls):
            if isinstance(val, _type) and issubclass(val, Parametric):
                if nested:
                    params[name] = val.defaultparams(nested=nested, type=type)
            elif type is not None:
                if isinstance(val, type):
                    params[name] = val
            elif isinstance(val, basic_types):
                params[name] = val
            elif isinstance(val, Descriptor):
                params[name] = val.default
        return params


class Defer(object):

    """
    Callback registry.

    Example
    -------
    >>> defer = Defer()
    >>> @defer(1, y=2)
    ... def _(x, y):
    ...     print('x:', x, ' ', 'y:', y)
    ...
    >>> defer.call()
    x: 1   y: 2

    Once the callbacks are called, they are cleared from the registry.

    >>> defer.call()

    Of coerce, decorator syntax is not mandatory:

    >>> defer('x:', 1)(print)                          # doctest: +ELLIPSIS
    <function ...>
    >>> defer.call()
    x: 1

    .. To make the following doctest reproducible, let's do this:

       >>> from collections import OrderedDict
       >>> defer.callbacks = OrderedDict()

    The callback registry can be categorized with keys:

    >>> for i in range(3):
    ...     for v in 'xy':
    ...         _ = defer.keyed(('cat', i), v, '=', i)(print)
    ...

    One category can be run by specifying ``key`` argument of `.call`.

    >>> defer.call(('cat', 1))
    x = 1
    y = 1

    Calling without ``key`` argument means "call everything".  Note
    that the category 1 callbacks are not called below, since they
    were already called.

    >>> defer.call()
    x = 0
    y = 0
    x = 2
    y = 2

    """

    def __init__(self):
        self.callbacks = {}

    def keyed(self, key, *args, **kwds):
        """
        Register a callback with `key`.
        """
        def decorator(teardown):
            def wrapper():
                teardown(*args, **kwds)
            self.callbacks.setdefault(key, []).append(wrapper)
            return wrapper
        return decorator

    def __call__(self, *args, **kwds):
        """
        Register a callback.
        """
        return self.keyed(None, *args, **kwds)

    def call(self, key=None):
        """
        Call deferred callbacks and un-register them.
        """
        if key is None:
            cbs = self.callbacks.values()
            callbacks = list(itertools.chain.from_iterable(cbs))
            self.callbacks.clear()
        else:
            callbacks = self.callbacks.pop(key)
        for c in callbacks:
            try:
                c()
            except Exception as err:
                logger.exception(err)


class Executable(Parametric):

    """
    The base class supporting execution and plugin mechanism.

    Example
    -------
    >>> class MyPlugin(Plugin):
    ...     def pre_run(self):
    ...         print('Pre-run:', self.__class__.__name__)
    ...
    >>> class MyExec(Executable):
    ...     myplugin = MyPlugin
    ...
    ...     def run(self):
    ...         print('Run:', self.__class__.__name__)
    ...
    >>> excbl = MyExec()
    >>> excbl.execute()
    Pre-run: MyPlugin
    Run: MyExec

    """

    def __init__(self, *args, **kwds):
        super(Executable, self).__init__(*args, **kwds)
        self.defer = Defer()

    def execute(self, *args):
        try:
            self.prepare()
            call_plugins(self, 'prepare')
            if self.is_loadable():
                self.load()
            else:
                call_plugins(self, 'pre_run')
                self.run(*args)
                call_plugins(self, 'post_run')
                self.save()
                call_plugins(self, 'save')
            call_plugins(self, 'finish')
            self.finish()
        # except Exception as err:
        #     self.onerror(err)
        #     raise
        finally:
            self.defer.call()

    def is_loadable(self):
        """
        |TO BE EXTENDED| Return `True` if `self` is loadable.

        Default is to return `False` always.

        """
        return False

    def prepare(self):
        """
        |TO BE EXTENDED| Do anything to be done before `run`.
        """

    def run(self, *args):
        """
        |TO BE EXTENDED| Do the actual simulation/analysis.
        """

    def save(self):
        """
        |TO BE EXTENDED| Save the result manually.
        """

    def load(self):
        """
        |TO BE EXTENDED| Load saved result manually.
        """

    def finish(self):
        """
        |TO BE EXTENDED| Do anything to be done before exit.
        """


def call_plugins(self, method):
    for plugin in attrs_of(self, Plugin):
        getattr(plugin, method)()


class Plugin(Parametric):

    """
    Plugin base class.
    """

    def __init__(self, *args, **kwds):
        super(Parametric, self).__init__(*args, **kwds)
        self.defer = Defer()

    def prepare(self):
        pass

    def pre_run(self):
        pass

    def post_run(self):
        pass

    def save(self):
        pass

    def load(self):
        pass

    def finish(self):
        pass
