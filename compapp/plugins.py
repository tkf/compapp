import os

from .core import Plugin
from .properties import Link, Delegate, Owner, OwnerInfo, Required


class BaseDataStore(Plugin):
    pass


class DirectoryDataStore(Plugin):
    dir = Required(str)

    def prepare(self):
        os.makedirs(self.dir)


class SubDataStore(BaseDataStore):

    datastore = Delegate()
    ownerinfo = OwnerInfo()

    def path(self, *args, **kwds):
        # but how about List/Dict?
        return self.path(self.name, *args, **kwds)


class HashDataStore(Plugin):
    basedir = Required(str)
    owner = Owner()

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
    handler = Link('#.logger.handler')

    def prepare(self):
        path = self.datastore.path('run.log')
        self.setup_file_stream_handler(path)


class Debug(Plugin):

    """
    Example
    -------
    ::

      class MySimulator(Simulator):
          dbg = Debug()

          def run(self):
              tmp = calculate()
              self.dbg.tmp = tmp
              self.result = tmp / len(tmp)

    The assignment ``self.dbg.tmp = tmp``:

    - triggers ``logger.debug(...)``
    - holds the value if debug flag is provided

    """

    logger = Delegate()


class AutoDump(Plugin):

    """

    - `numpy.savez`
    - :ref:`pandas.HDFStore <pandas:io.hdf5>`

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

    datastore = SubDataStore()
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
    """


class RecordTiming(Plugin):

    """
    """


class PluginWrapper(Plugin):

    """
    """
