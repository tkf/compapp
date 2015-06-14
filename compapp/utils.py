from .core import Executable
from .plugins import PluginWrapper, AutoDump, Figure, \
    SubDataStore, HashDataStore


class Plotter(Executable):

    """
    Base plotter class.

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
              self.density.plot(self.simulator)
              self.dist.plot(self.simulator)

    Then ``myapp.py --datastore.dir out/`` saves density plot in
    ``out/density/0.png`` and cumulative distribution in
    ``out/dist/0.png``.

    """

    figure = Figure
    datastore = SubDataStore


class Simulator(Executable):

    """
    Base simulator class.

    .. todo:: Do I need it?  Why not just use `.SimulationApp`?

    .. todo:: If I were to use this class, it's better to have
       `result_names` stuff implemented in `.Application`.
       Maybe separate that part into a class `Calculator` and
       inherit from `Simulator` and `.Application`.

    """

    datastore = SubDataStore

    class plugins(PluginWrapper):
        autodump = AutoDump


class Analyzer(Simulator):

    datastore = HashDataStore
