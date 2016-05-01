import itertools
import logging


logger = logging.getLogger(__name__)


class Parameter(object):
    pass


simple_types = (
    complex,
    float,
    int,
    long,
    str,
    unicode,
    bool,
)

basic_types = simple_types + (tuple, list, dict, set)
"""
Basic Python types.
"""


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
    >>> setattr(mp, 'param.b', -1)
    >>> mp.param.b
    -1
    >>> getattr(mp, 'param.a')
    0

    **Automatic parameter mix-in.**
    If it is just for resetting parameter, you don't need to inherit
    nested `Parametric` classes; it happens automatically.

    >>> class Base(Parametric):
    ...     class x(Parametric):
    ...         i = 0
    ...         j = 1
    ...
    ... class Another(Base):
    ...     class x(object):  # do not need to inherit Base.x
    ...         i = -1
    ...
    >>> par = Another()
    >>> par.x.i
    -1
    >>> par.x.j
    1

    """

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

        """

    @classmethod
    def paramnames(cls, type=None):
        """
        List names of parameter for this class.

        User sub-class can modify own behavior by overriding this
        method.

        """

    @classmethod
    def defaultparams(cls, nested=False, type=None):
        """
        Get default parameters as a `dict`.
        """


class Defer(object):

    def __init__(self):
        self.callbacks = {}

    def keyed(self, key, *args, **kwds):
        """
        Register a callback with `key`.
        """
        def decorator(teardown):
            return lambda: teardown(*args, **kwds)
        self.callbacks.setdefault(key, []).append(decorator)
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
            callbacks = itertools.chain.from_iterable(self.callbacks.values())
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
    """

    def execute(self, *args):
        try:
            self.prepare_all()
            if self.is_loadable():
                self.load()
            else:
                self.run_all(*args)
                self.save_all()
            self.finish()
        # except Exception as err:
        #     self.onerror(err)
        #     raise
        finally:
            self.defer.call()

    def prepare(self):
        """
        |TO BE EXTENDED| Do anything to be done before `run`.
        """

    def prepare_plugins(self):
        """ Call 'prepare' hook of plugins. """
        call_plugins(self, 'prepare')

    def prepare_all(self):
        self.prepare_plugins()
        self.prepare()

    def pre_run(self):
        call_plugins(self, 'pre_run')

    def run(self, *args):
        """
        |TO BE EXTENDED| Do the actual simulation/analysis.
        """

    def post_run(self):
        call_plugins(self, 'post_run')

    def run_all(self, *args):
        self.pre_run()
        self.run(*args)
        self.post_run()

    def save(self):
        """
        |TO BE EXTENDED| Save the result manually.
        """

    def save_all(self):
        self.save()
        self.save_plugins()

    def save_plugins(self):
        call_plugins(self, 'save')

    def load(self):
        """
        |TO BE EXTENDED| Load saved result manually.
        """

    def finish(self):
        """
        |TO BE EXTENDED| Do anything to be done before exit.
        """

    def finish_plugins(self):
        call_plugins(self, 'finish')

    def finish_all(self):
        self.finish()
        self.finish_plugins()


def call_plugins(self, method):
    for plugin in self.params(type=Plugin):
        getattr(plugin, method)()


class Plugin(Parametric):

    """
    Plugin base class.
    """

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
