import copy
import itertools
import os
import logging
import logging.config
import weakref

from ..base import Unspecified, props_of
from ..core import simple_types, private
from ..interface import Plugin, Executable, call_plugins
from ..descriptors import Link, Delegate, Or, Choice, OfType, List, Dict


_loglevels = ['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN',
              'INFO', 'DEBUG', 'NOTSET']


def _loglevel(default=Unspecified, *alternatives):
    levels = _loglevels + list(map(str.lower, _loglevels))
    ts = (Choice(*levels, nodefault=True), OfType(int)) + alternatives
    return Or(*ts, default=default)


def _level_as_int(lvl):
    if isinstance(lvl, int):
        return lvl
    return getattr(logging, lvl.upper())


class Logger(Plugin):

    r"""
    Interface to pre-configured `logging.Logger`.

    It does the following automatically:

    - make a logger with an appropriate dotted name
    - set up handler

    .. Some infernal hack to make the doctest consistent:
       >>> Logger._idgen = itertools.count()

    >>> from compapp import Computer
    >>> class MyAppForLoggerDemo(Computer):
    ...     def run(self):
    ...         self.log.error('error message')
    ...         self.log.info('info message')
    >>> app = MyAppForLoggerDemo()
    >>> app.log.formatters['default']['format'] = \
    ...     '%(levelname)s %(name)s | %(message)s'
    >>> app.log.handlers['console']['stream'] = 'ext://sys.stdout'
    >>> app.execute()
    ERROR compapp.plugins.misc.MyAppForLoggerDemo.0 | error message

    .. attribute:: log

       An instance of `logging.Logger`.
       This is accessible in and after `.Executable.run` or
       `.Executable.load` hooks.

       .. todo:: Make it accessible all the time.

    .. attribute:: critical
                   error
                   warn
                   info
                   debug

       Shortcut for `.log`\ `.debug <logging.Logger.debug>` etc.

    """

    configurator = Or(OfType(logging.config.BaseConfigurator),
                      Link('...log.configurator'),
                      isparam=False)

    handlers = Or(List(str),
                  Dict(str, Dict(str, simple_types)),
                  Link('...log.handlers'),
                  # Next Dict trait is same as the one above; it's
                  # just for holding the default value.  Dict is used
                  # instead of passing `default=` to Or to make a new
                  # instance for each instance of Logger.
                  Dict(str, Dict(str, simple_types), default=dict(
                      console={
                          'class': 'logging.StreamHandler',
                          'formatter': 'default',
                          'stream': 'ext://sys.stderr',
                      },
                      file={
                          'class': 'logging.FileHandler',
                          'formatter': 'verbose',
                          'datastore': True,
                          'filename': 'run.log',
                      })))
    """
    The dictionary *handlers* of the `logging configuration
    dictionary`_.  Each handler may contain a special configuration
    ``'datastore': True`` indicating that this handler is configured
    only if datastore is accessible.  For nested classes, this
    attribute is ignored if `.ownconfig` is not `True` (default is
    ``'auto'``).

    .. _`logging configuration dictionary`: https://docs.python.org/library/logging.config.html#dictionary-schema-details
    """

    formatters = Dict(str, Dict(str, str), default=dict(
        basic=dict(format=logging.BASIC_FORMAT),
        default=dict(
            format='%(levelname)s %(asctime)s %(name)s | %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S",
        ),
        verbose=dict(
            format='%(asctime)s:' + logging.BASIC_FORMAT,
        ),
    ))
    """
    The dictionary *formatters* of the `logging configuration
    dictionary`_.  See also `.handlers`.
    """

    ownconfig = Choice('auto', True, False)
    """
    If ``'auto'`` (default), configure handlers if the owner is the
    root app and reuse the handlers of owner's logger otherwise.  The
    value `True` forces this logger plugin to make own handlers.  The
    value `False` forces the reuse (which is an error if the owner is
    the root app).
    """

    level = Or(_loglevel(), Link('...log.level'), default='ERROR')
    """
    Logger level.  Default is ``'ERROR'``.
    """

    critical = Link('.logger.critical')
    error = Link('.logger.error')
    warn = Link('.logger.warn')
    info = Link('.logger.info')
    debug = Link('.logger.debug')

    datastore = Delegate()

    nametemplate = '{self.__class__.__module__}.{self.__class__.__name__}.{id}'
    _idgen = itertools.count()

    def prepare(self):
        self.logger = logging.getLogger(self.nametemplate.format(
            self=private(self).owner, id=next(self._idgen)))
        self.logger.setLevel(_level_as_int(self.level))

        if self.should_configure():
            assert isinstance(self.handlers, dict)
            self.configure()
        handlers = list(self.configurator.config['handlers'])
        self.configurator.add_handlers(self.logger, handlers)

    def configure(self):
        messages = []
        handlers = copy.deepcopy(self.handlers)
        is_writable = (hasattr(self, 'datastore') and
                       self.datastore.is_writable())
        for key, hndlr in list(handlers.items()):
            if hndlr.pop('datastore', False):
                if is_writable:
                    filename = self.datastore.path(hndlr['filename'],
                                                   mkdir=False)
                    if not os.path.exists(filename) or \
                            os.access(filename, os.W_OK):
                        hndlr['filename'] = \
                            self.datastore.path(hndlr['filename'])
                        continue
                    messages.append(
                        "Handler {key} cannot be configured since "
                        " {filename} is not writable.".format(
                            key=key, filename=filename))
                del handlers[key]

        self.configurator = logging.config.DictConfigurator(dict(
            version=1,
            formatters=self.formatters,
            handlers=handlers,
            disable_existing_loggers=False,
        ))
        self.configurator.configure()
        for m in messages:
            self.warn(m)

    def should_configure(self):
        if self.ownconfig == 'auto':
            return not hasattr(self, 'configurator')
        return self.ownconfig


class DebugNS(object):

    def __init__(self, debug):
        self.__debug = weakref.proxy(debug)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(DebugNS, self).__setattr__(name, value)
        if self.__debug.is_enabled():
            if self.__debug.is_logging_debug():
                self.__debug.log.debug('{0} = {1!r}'.format(name, value))
            super(DebugNS, self).__setattr__(name, value)


class Debug(Plugin):

    r"""
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

    >>> from compapp import Computer
    >>> class MySimulator(Computer):
    ...
    ...     def run(self):
    ...         tmp = list(range(3))
    ...         self.dbg.tmp = tmp
    ...         self.results.div = [x / len(tmp) for x in tmp]
    ...
    >>> app = MySimulator()
    >>> app.log.level = 'DEBUG'

    Before ``app.execute()``, let's tweak logger output so
    that output is concise:

    >>> app.log.formatters['default']['format'] = \
    ...     '%(levelname)s %(name)s | %(message)s'
    >>> app.log.handlers['console']['stream'] = 'ext://sys.stdout'

    .. Some infernal hack to make the doctest consistent:
       >>> app.log._idgen = itertools.count()

    Finally...:

    >>> app.execute()                                  # doctest: +ELLIPSIS
    DEBUG compapp.plugins.misc.MySimulator.0 | ...
    DEBUG compapp.plugins.misc.MySimulator.0 | tmp = [0, 1, 2]
    DEBUG compapp.plugins.misc.MySimulator.0 | ...

    >>> app.dbg.tmp
    [0, 1, 2]

    Note that executing the same app without ``.log.level = 'DEBUG'``
    suppress the logging and storing the temporary variable.  The
    Debug plugin also can be disabled independent of the log level by
    setting its `.enable` to `False`.

    >>> app = MySimulator()
    >>> app.execute()
    >>> app.dbg.tmp
    Traceback (most recent call last):
      ...
    AttributeError: 'DebugNS' object has no attribute 'tmp'

    """

    log = Link('..log')
    enable = Choice('auto', True, False)
    """
    If ``'auto'`` (default), enable this plugin if the log level of
    `Logger` plugin is ``'DEBUG'`` or lower.  `True` (`False`) enables
    (disables) this plugin independent of the log level.
    """

    def __init__(self, *args, **kwds):
        super(Debug, self).__init__(*args, **kwds)
        self.ns = DebugNS(self)

    def is_logging_debug(self):
        return hasattr(self, 'log') and \
            self.log.logger.getEffectiveLevel() <= logging.DEBUG

    def is_enabled(self):
        if self.enable == 'auto':
            return self.is_logging_debug()
        return self.enable


class Figure(Plugin):

    r"""
    A wrapper around `matplotlib.pyplot.figure`.

    Automatically save and (optionally) show the figure at the end of
    execution.

    Examples
    --------

    Normally, `Figure` is prepared by an `.Executable` subclass such
    as `.Computer`.  To manually play with `Figure`, it is equivalent
    to do:

    >>> figure = Figure()
    >>> figure.prepare()

    `Calling <__call__>` a `Figure` instance gives you a matplotlib
    figure.

    >>> figure()                                       # doctest: +ELLIPSIS
    <matplotlib.figure.Figure object at ...>

    It also has `.subplots` which is just a thin wrapper around
    `matplotlib.pyplot.subplots`:

    >>> fig, (ax1, ax2) = figure.subplots(2)

    .. Manually close:
       >>> figure.defer.call()


    Suppose you have a nested `.Computer`\ s:

    >>> from compapp.apps import Computer
    >>> class MyApp(Computer):
    ...     class sub(Computer):
    ...         class sub(Computer):
    ...             pass

    .. glossary::

       Global `.Figure` plugin configuration

         The attribute `.autoclose` is `.Link`\ ed to the plugin of
         the owner `Computer`.  It makes possible to configure
         `Figure` plugins "globally":

    >>> app = MyApp()
    >>> app.sub.figure.autoclose  # default value
    True
    >>> app.figure.autoclose = False
    >>> app.sub.figure.autoclose
    False
    >>> app.sub.sub.figure.autoclose
    False

    A "sub-tree" of the `.Computer`\ s can be configured separately:

    >>> app.sub.figure.autoclose = True
    >>> app.sub.sub.figure.autoclose
    True
    >>> app.figure.autoclose
    False

    Similar global/sub-tree configuration mechanism works for the
    `.show` attribute:

    >>> app.figure.show  # default value
    False
    >>> app.figure.show = True
    >>> app.sub.figure.show
    True
    >>> app.sub.sub.figure.show
    True

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> import os
    >>> from compapp import Computer
    >>> class MyApp(Computer):
    ...     def run(self):
    ...         self.figure()
    ...         self.figure(name='alpha')
    ...         self.figure(name='beta')
    ...
    >>> app = MyApp()
    >>> app.datastore.dir = 'out'
    >>> app.execute()
    >>> sorted(f for f in os.listdir('out') if f.startswith('figure-'))
    ['figure-0.png', 'figure-alpha.png', 'figure-beta.png']

    See also
    --------
    :ref:`ex-simple_plots`
    :ref:`ex-named_figure`

    """

    ext = 'png'

    datastore = Delegate()
    r"""
    `.Delegate`\ ed attribute accessing to a `.BaseDataStore`.
    """

    show = Or(OfType(bool), Link('...figure.show'), default=False)
    """
    Automatically call `matplotlib.pyplot.show` if `True`.  The
    default is `False`, if not specified by the :term:`owner class`.
    See: :term:`Global Figure plugin configuration`.
    """

    autoclose = Or(OfType(bool), Link('...figure.autoclose'), default=True)
    """
    Automatically close matplotlib figures if `True` which is the
    default, if not specified by the :term:`owner class`.
    See: :term:`Global Figure plugin configuration`.
    """

    def prepare(self):
        self._figures = {}
        self._num = 0

    def register(self, fig, name=None):
        """
        Register `fig` so that it is automatically saved, showed and closed.
        """
        self._set_fig(name, fig)

    def _set_fig(self, name, fig):
        from matplotlib import pyplot

        if name is None:
            while str(self._num) in self._figures:
                self._num += 1
            name = str(self._num)
            self._num += 1
        assert isinstance(name, str)

        self._figures[name] = fig

        @self.defer.keyed('save')
        def _():
            if not (hasattr(self, 'datastore') and
                    self.datastore.is_writable()):
                return
            path = self.datastore.path(name + '.' + self.ext)
            fig.savefig(path)

        if self.autoclose:
            self.defer(fig)(pyplot.close)

        return fig

    def __call__(self, *args, **kwds):
        """
        Make a new matplotlib figure.

        All the positional and keyword arguments are passed to
        `matplotlib.pyplot.figure` except one keyword argument *name*.

        Parameters
        ----------
        name : str, int, or None
            Unique name of the figure.  It is an error to call this
            method with the same *name* twice.

        Returns
        -------
        fig : matplotlib.figure.Figure

        """
        from matplotlib import pyplot
        name = kwds.pop('name', None)
        assert name not in self._figures
        return self._set_fig(name, pyplot.figure(*args, **kwds))

    def __getitem__(self, name):
        """
        Make a new matplotlib figure or get the new one.

        Examples
        --------
        The usual preparation (see: `Figure`):

        >>> figure = Figure()
        >>> figure.prepare()

        If figure is created with a name, it can be accessed by the
        dict-like interface:

        >>> fig_a = figure(name='a')
        >>> assert fig_a is figure['a']  # access an existing figure
        >>> fig_b = figure['b']  # create a new figure
        >>> assert fig_b is figure['b']

        Note that a new figure is created always when *name* is
        `None`:

        >>> assert figure[None] is not figure[None]

        .. Manually close:
           >>> figure.defer.call()

        Parameters
        ----------
        name : str, int, or None
            Unique name of the figure.

        Returns
        -------
        fig : matplotlib.figure.Figure

        """
        from matplotlib import pyplot

        try:
            return self._figures[name]
        except KeyError:
            pass

        return self._set_fig(name, pyplot.figure())

    def save(self):
        self.defer.call('save')

    def finish(self):
        if self.show:
            from matplotlib import pyplot
            pyplot.show()

    def subplots(self, *args, **kwds):
        """
        Wrapper around `matplotlib.pyplot.subplot`.

        All the positional and keyword arguments are passed to
        `matplotlib.pyplot.subplot` except one keyword argument
        *name*.

        Parameters
        ----------
        name : str, int, or None
            Unique name of the figure.  It is an error to call this
            method with the same *name* twice.

        Returns
        -------
        fig : `matplotlib.figure.Figure`
        ax : `matplotlib.axes.Axes` or `tuple`

        """
        from matplotlib import pyplot
        name = kwds.pop('name', None)
        assert name not in self._figures
        ret = fig, _ = pyplot.subplots(*args, **kwds)
        self._set_fig(name, fig)
        return ret


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
        executables = list(props_of(owner, Executable))
        while executables:
            for i, excbl in enumerate(executables):
                if self.is_runnable(excbl):
                    break
            else:
                return
            del executables[i]
            excbl.execute()


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


def real_owner(self):
    owner = private(self).owner
    if isinstance(owner, PluginWrapper):  # FIXME: ugly special case
        owner = private(owner).owner
    return owner
