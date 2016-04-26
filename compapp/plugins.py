import os

from .core import Plugin
from .properties import Link, Delegate, Owner, OwnerInfo, Required, Or


class BaseDataStore(Plugin):
    pass


class DirectoryDataStore(BaseDataStore):

    """
    Data-store using a directory.

    Examples
    --------

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    >>> mp = MyParametric({'datastore.dir': 'out'})
    >>> mp.path('file')
    'out/file'

    If a :term:`nested class` uses `DirectoryDataStore`, the path is
    automatically allocated under the `.dir` of the :term:`owner
    class`.

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    ...     class nested(Parametric):
    ...         datastore = DirectoryDataStore
    ...
    >>> mp = MyParametric({'datastore.dir': 'out'})
    >>> mp.nested.datastore.path()
    'out/nested'
    >>> mp.nested.datastore.path('file')
    'out/nested/file'
    >>> mp.nested.datastore.path('dir', 'file')
    'out/nested/dir/file'

    """

    def __dir_adapter(self, value):
        # In the above example:
        #    value == 'out'
        #    self.ownerinfo.name == 'nested'
        return os.path.join(self.ownerinfo.name, value)

    dir = Or(Delegate(adapter=__dir_adapter), Required(str))
    ownerinfo = OwnerInfo()
    overwrite = True
    clear_before_run = True

    def prepare(self):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)

    def path(self, *args, **kwds):
        """
        Path relative to the base directory `.dir`.

        Parameters
        ----------
        args : str
          Path relative to `.dir`.
          It will be joined by `os.path.join`.

        Keyword Arguments
        -----------------
        mkdir : bool
           If `True` (default), make the parent directory of returned
           `path` (i.e., ``os.path.dirname(path)``, not the `path`
           itself).

        Returns
        -------
        path : str
           ``os.path.join(self.dir, *args)``

        """
        def makepath(args, mkdir=True):
            path = os.path.join(self.dir, *args)
            dirname = os.path.dirname(path)
            if mkdir and not os.path.isdir(dirname):
                os.makedirs(dirname)
            return path
        return makepath(args, **kwds)


class SubDataStore(DirectoryDataStore):

    """
    Data-store using sub-paths of parent data-store.

    Examples
    --------

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    ...     class nested(Parametric):
    ...         datastore = SubDataStore
    ...
    >>> mp = MyParametric({'datastore.dir': 'out'})
    >>> mp.nested.datastore.path()
    'out/nested'
    >>> mp.nested.datastore.path('file')
    'out/nested-file'
    >>> mp.nested.datastore.path('dir', 'file')
    'out/nested-dir/file'
    >>> mp.nested.datastore.path('a', 'b', 'c')
    'out/nested-a/b/c'
    >>> mp.nested.sep = '.'
    >>> mp.nested.datastore.path('file')
    'out/nested.file'

    Since `DirectoryDataStore` already can be used for datastore using
    sub-directories, this class is specialized for the case using
    files under the directory of parent datastore.  If the
    :term:`owner class` of this datastore uses only a few files, it
    makes sense to not allocate a directory and to use this type of
    datastore.

    """

    # MAYBE: this class should be called ParasiteDataStore?

    dir = None  # null-out the dir parameter
    datastore = Link('...datastore')
    ownerinfo = OwnerInfo()
    sep = '-'

    def path(self, *args, **kwds):
        # but how about List/Dict?
        if not args:
            self.datastore.path(self.name)
        part0 = self.name + self.sep + args[0]
        return self.datastore.path(part0, *args[1:], **kwds)


class HashDataStore(DirectoryDataStore):

    """
    Automatically allocated data-store based on hash of parameter.
    """

    basedir = Required(str)
    owner = Owner()
    include_plugin_parameters = False

    def ownerhash(self):
        def not_datastore(key, value):
            pass
        params = self.owner.get_params(deep=True, include=not_datastore)
        ownerclass = type(self.owner)
        return self.sha1(ownerclass, params)

    def run(self):
        digest = self.ownerhash()
        path = os.path.join(self.basedir, digest[:2], digest[2:])
        os.makedirs(path)
        self.dir = path


class Logger(Plugin):

    """
    Interface to pre-configured `logging.Logger`.

    It does the following automatically:

    - make a logger with an appropriate dotted name
    - set up handler

    """

    handler = Link('#.logger.handler')
    # FIXME: how to resolve reference-to-self?

    def prepare(self):
        path = self.datastore.path('run.log')
        self.setup_file_stream_handler(path)


class Debug(Plugin):

    """
    Debug helper plugin.

    Since `.Application` does not allow random attributes to be set,
    it's hard to debug or interactively investigate simulation and
    analysis by storing temporary variable to the `.Application`
    instance.  `Debug` provides the place for that.

    - If `store` flag is *not* set, it does not store anything;
      assignment would be just no-op.  This is useful for debugging
      memory-consuming object.
    - If `logger` is defined, and its level is DEBUG, assignment
      to `Debug` object writes out debug message.

    Example
    -------
    ::

      class MySimulator(Simulator):
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


class AutoDump(Plugin):

    """
    Automatically save owner's results.

    Supported back-ends:

    - `json`
      for `dict`, `list` or `tuple`
    - `numpy.savez`
      for `numpy.ndarray`
    - :ref:`pandas.HDFStore <pandas:io.hdf5>`
      for pandas object

    Example
    -------
    ::

      class MyApp(Application):
          # Note: Application includes AutoDump by default

          def run(self):
              self.results.alpha = dict(pi='3.14')

    Then ``MyApp({'datastore.dir': 'OUT'}).execute()`` creates a JSON
    file at ``OUT/results.json`` with content ``{'alpha': {'pi':
    3.14}}``.

    """

    result_names = ('results',)
    """
    These attributes of the owner class are dumped.
    """


class Figure(Plugin):

    """
    A wrapper around `matplotlib.pyplot.figure`.

    Automatically save and (optionally) show the figure at the end of
    execution.

    Examples
    --------

    ::

      class MyPlotter(Executable):
          figure = Delegate()

          def run(self):
              fig = self.figure()
              ax = fig.add_subplot(111)
              ax.plot(...)

      class MyApp(Application):
          figure = Figure
          plotter = MyPlotter

    """

    datastore = Delegate()
    show = False

    def __call__(self, name=None):
        """
        Make a new matplotlib figure.

        Returns
        -------
        fig : matplotlib.figure.Figure
        """
        from matplotlib import pyplot
        fig = pyplot.figure()
        # FXIME: record `fig` to internal list etc.
        return fig

    def save(self):
        for (name, fig) in self.items():
            path = self.datastore.path(name + '.' + self.ext)
            fig.savefig(path)

    def finish(self):
        if self.show():
            from matplotlib import pyplot
            pyplot.show()

        for (name, fig) in self.items():
            fig.close()


class RecordVCS(Plugin):

    """
    Record VCS revision automatically.
    """

    vcs = 'git'


class RecordTiming(Plugin):

    """
    Record timing information.
    """

    def pre_run(self):
        pass

    def post_run(self):
        pass


class DumpParameters(Plugin):

    """
    Dump parameters used for its owner.
    """
    # FIXME: It should be included by default when `HashDataStore` is
    #        used.  How to avoid running it twice (i.e.,
    #        `DumpParameters` explicitly specified and the one called
    #        via `HashDataStore`)?


class PluginWrapper(Plugin):

    """
    Combine multiple plugins into one plugin.

    Some plugin such as `AutoDump` has no "interface" and just works
    behind-the-scene.  In this case, having ``MyApp.autodump =
    AutoDump`` is just wasting user's name-space.  This class avoid
    this by moving all those behind-the-scene plugins into one name.
    See `.Application.plugin` for its use-case.

    """
