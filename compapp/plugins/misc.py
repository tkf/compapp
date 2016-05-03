from ..core import call_plugins, private, Plugin, Executable
from ..descriptors import Link, Delegate


class Logger(Plugin):

    """
    Interface to pre-configured `logging.Logger`.

    It does the following automatically:

    - make a logger with an appropriate dotted name
    - set up handler

    """

    datastore = Delegate()
    handler = Link('logger.handler')
    # FIXME: how to resolve reference-to-self?

    def prepare(self):
        return                  # FIXME: Implement Logger.prepare
        path = self.datastore.path('run.log')
        self.setup_file_stream_handler(path)


class Debug(Plugin):

    """
    Debug helper plugin.

    Since `.Computer` does not allow random attributes to be set,
    it's hard to debug or interactively investigate simulation and
    analysis by storing temporary variable to the `.Computer`
    instance.  `Debug` provides the place for that.

    - If `store` flag is *not* set, it does not store anything;
      assignment would be just no-op.  This is useful for debugging
      memory-consuming object.
    - If `logger` is defined, and its level is DEBUG, assignment
      to `Debug` object writes out debug message.

    Example
    -------
    ::

      class MySimulator(Computer):
          dbg = Debug

          def run(self):
              tmp = calculate()
              self.dbg.tmp = tmp
              self.result = tmp / len(tmp)

    The assignment ``self.dbg.tmp = tmp``:

    - triggers ``logger.debug(...)``
    - holds the value if debug flag is provided

    """

    logger = Delegate()
    store = True


class Figure(Plugin):

    """
    A wrapper around `matplotlib.pyplot.figure`.

    Automatically save and (optionally) show the figure at the end of
    execution.

    Examples
    --------

    .. plot::
       :include-source:

       from compapp.apps import Computer

       class MyApp(Computer):
           def run(self):
               fig = self.figure()
               ax = fig.add_subplot(111)
               ax.plot([x ** 2 for x in range(100)])

       MyApp().execute()

    """

    datastore = Delegate()
    show = False

    def prepare(self):
        self._figures = {}
        self._num = 0

    def __call__(self, name=None):
        """
        Make a new matplotlib figure.

        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        from matplotlib import pyplot

        if name is None:
            while str(self._num) in self._figures:
                self._num += 1
            name = str(self._num)
            self._num += 1
        assert isinstance(name, str)

        try:
            return self._figures[name]
        except KeyError:
            pass

        self._figures[name] = fig = pyplot.figure()

        @self.defer.keyed('save')
        def _():
            path = self.datastore.path(name + '.' + self.ext)
            fig.savefig(path)

        self.defer(fig)(pyplot.close)

        return fig

    def save(self):
        self.defer.call('save')

    def finish(self):
        if self.show:
            from matplotlib import pyplot
            pyplot.show()


def is_runnable(excbl):
    if getattr(excbl, 'argrange', (None, None))[0] != 0:
        return False
    for name in excbl.paramnames(type=Link):
        if not hasattr(excbl, name):
            return False
    # All the links are accessible, meaning that all
    # "implicit upstreams" are already run.
    return True


class AutoUpstreams(Plugin):

    """
    Automatically execute upstreams.
    """

    @staticmethod
    def is_runnable(excbl):
        return getattr(excbl, 'is_runnable', lambda: is_runnable(excbl))()

    def prepare(self):
        owner = private(self).owner
        executables = owner.params(type=Executable)
        while executables:
            for i, ebl in executables:
                if self.is_runnable(ebl):
                    break
            else:
                return
            del executables[i]
            self.execute()


class PluginWrapper(Plugin):

    """
    Combine multiple plugins into one plugin.

    Some plugin such as `AutoDump` has no "interface" and just works
    behind-the-scene.  In this case, having ``MyApp.autodump =
    AutoDump`` is just wasting user's name-space.  This class avoid
    this by moving all those behind-the-scene plugins into one name.
    See `.Computer.plugin` for its use-case.

    """

    def __getattr__(self, name):
        return getattr(private(self).owner, name)


def makemethod(method):
    def func(self):
        call_plugins(self, method)
    return func


for method in set(dir(Plugin)) - set(dir(Plugin.mro()[1])):
    if method.startswith('_'):
        continue
    setattr(PluginWrapper, method, makemethod(method))
del method
