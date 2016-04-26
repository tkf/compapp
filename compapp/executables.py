"""
Executable subclasses.
"""


from .core import Executable
from .plugins import PluginWrapper, AutoDump, Figure, \
    SubDataStore, DirectoryDataStore, HashDataStore


class Simulator(Executable):

    """
    Run computations solely depending on parameters.

    .. todo:: Do I need it?  Why not just use `.SimulationApp`?

    .. todo:: If I were to use this class, it's better to have
       `result_names` stuff implemented in `.Application`.
       Maybe separate that part into a class `Calculator` and
       inherit from `Simulator` and `.Application`.

    """

    datastore = DirectoryDataStore

    class plugins(PluginWrapper):
        autodump = AutoDump

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

    plugins = None  # null-out plugins
    """
    Since no heavy computations are needed, `.AutoDump` plugin is not
    included.
    """


class Analyzer(Executable):

    """
    Run computations depending on data from other :term:`data source`.
    """

    datastore = HashDataStore

    class plugins(PluginWrapper):
        autodump = AutoDump

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
