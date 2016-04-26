"""
Executable subclasses.
"""


from .core import Executable
from .plugins import PluginWrapper, Figure, \
    BaseDataStore, SubDataStore, DirectoryDataStore, HashDataStore


class MagicPlugins(PluginWrapper):
    from .plugins import (
        AutoDump as autodump,
        RecordVCS as recordvcs,
        RecordTiming as recordtiming,
        DumpParameters as dumpparameters,
    )


class Computer(Executable):

    """
    `.Executable` bundled with useful plugins.

    Examples
    --------

    **Strict attribute.**
    `Computer` subclass does not allow setting attribute other than
    its parameter or result (specified by :attr:`result_names`).  This
    makes sure that `Computer` holds the same data after `run` and
    `load`.  To save intermediate data for debugging for interactive
    use, set it to :attr:`dbg` (instance of `.Debug`).

    >>> class MyApp(Computer):
    ...    result_names = ('alpha', 'beta')
    >>> app = MyApp()
    >>> app.alpha = 1.0
    >>> app.gamma
    Traceback (most recent call last):
      ...
    AttributeError: 'MyApp' object has no attribute 'gamma'

    """

    result_names = ()
    """
    Names of attributes allowed to be set.  A list of `str`.
    """

    magics = MagicPlugins
    """
    Plugins that work behind the scene.
    """

    from .plugins import (
        Debug as dbg,
        Figure as figure,
        Logger as logger,
    )

    datastore = BaseDataStore
    r"""
    This is a "conventional" property in the sense `Computer` class
    itself is not aware of this property.  However, this is the most
    heavily used property accessed by many sub-`.Executable`\ s and
    `.Plugin`\ s.  Those "users" of `datastore` property expects it to
    be a subclass of `.BaseDataStore`.
    """


class Simulator(Computer):

    """
    Run computations solely depending on parameters.

    Note that usually user should subclass `.SimulationApp` (which is
    a subclass of this class) rather than this `Simulator` class since
    `.SimulationApp` has richer functionalities.

    """

    datastore = DirectoryDataStore

    def run_all(self):
        self.pre_run()
        self.run()
        self.post_run()

    def run(self):
        """
        |TO BE EXTENDED| Do the actual simulation.
        """

    def execute(self, **kwds):
        assert 'data' not in kwds
        super(Simulator, self).execute(**kwds)


class DataLoader(Simulator):
    """
    :term:`Data source` loaded from disk.
    """

    class magics(MagicPlugins):
        autodump = None  # null-out
    """
    Since no heavy computations are needed, `.AutoDump` plugin is not
    included.
    """

    datastore = SubDataStore


class Analyzer(Computer):

    """
    Run computations depending on data from other :term:`data source`.
    """

    datastore = HashDataStore

    def execute(self, data, **kwds):
        super(Analyzer, self).execute(data, **kwds)

    def run(self, data):
        """
        |TO BE EXTENDED| Do the actual analysis of `data`.
        """


class Plotter(Analyzer):

    """
    An `.Analyzer` subclass specialized for plotting.

    Example
    -------
    ::

      class DensityPlotter(Plotter):
          pass

      class CumulativeDistributionPlotter(Plotter):
          pass

      class MyApp(SimulationApp):
          density = DensityPlotter
          dist = CumulativeDistributionPlotter

          def run(self):
              self.simulator.execute()
              self.density.execute(self.simulator)
              self.dist.execute(self.simulator)

    Then ``myapp.py --datastore.dir out/`` saves density plot in
    ``out/density-0.png`` and cumulative distribution in
    ``out/dist-0.png``.

    """

    figure = Figure
    datastore = SubDataStore
