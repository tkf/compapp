class Parameter(object):
    pass


simple_types = (
    complex,
    float,
    int,
    long,
    str,
    unicode,
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

    """

    def get_params(self, deep=False, type=None):
        """
        Get parameters as a `dict`.

        Parameters
        ----------
        deep : bool
            if true, return a nested `dict` for `Parametric`
            properties.
        type
            type of parameters to be returned

        Returns
        -------
        params : dict

        """

    @classmethod
    def get_param_names(cls, type=None):
        """
        List names of parameter for this class.

        User sub-class can modify own behavior by overriding this
        method.

        """

    @classmethod
    def get_param_defs(cls, deep=False, type=None):
        """
        Get parameter "definitions" as a `dict`.
        """


class Executable(Parametric):

    """
    The base class supporting execution and plugin mechanism.
    """

    def execute(self, finish=True):
        self.prepare_all()
        if self.is_loadable():
            self.load()
        else:
            self.run_all()
            self.save_all()
        if finish:
            self.finish_all()

    def upstreams(self):
        """
        [TO BE OVERRIDE]
        """

    def prepare(self):
        """
        [TO BE OVERRIDE]
        """

    def prepare_plugins(self):
        """ Call 'prepare' hook of plugins. """
        call_plugins(self, 'prepare')

    def prepare_upstreams(self):
        r"""
        Execute (load or run) upstream `Executable`\ 's.
        """
        for name in self.upstreams():
            upstream = getattr(self, name)
            upstream.execute(finish=False)

    def prepare_all(self):
        self.prepare_plugins()
        self.prepare_upstreams()
        self.prepare()

    def pre_run(self):
        call_plugins(self, 'pre_run')

    def run(self):
        """
        [TO BE OVERRIDE]
        """

    def post_run(self):
        call_plugins(self, 'post_run')

    def run_all(self):
        self.pre_run()
        self.run()
        self.post_run()

    def save(self):
        """
        [TO BE OVERRIDE]
        """

    def save_all(self):
        self.save()
        self.save_plugins()

    def save_plugins(self):
        call_plugins(self, 'save')

    def load(self):
        """
        [TO BE OVERRIDE]
        """

    def finish(self):
        """
        [TO BE OVERRIDE]
        """

    def finish_plugins(self):
        call_plugins(self, 'finish')

    def finish_all(self):
        self.finish()
        self.finish_plugins()
        self.finish_upstreams()


def call_plugins(self, method):
    for plugin in self.get_params(type=Plugin):
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
