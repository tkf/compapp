"""
Executable subclasses.
"""


from .core import Executable
from properties import Instance
from .plugins import PluginWrapper, Figure, \
    SubDataStore, DirectoryDataStore, HashDataStore


class DictObject(object):  # TODO: implement dict-object hybrid
    pass


class MagicPlugins(PluginWrapper):
    from .plugins import (
        AutoDump as autodump,
        RecordVCS as recordvcs,
        RecordTiming as recordtiming,
        DumpParameters as dumpparameters,
        AutoUpstreams as autoupstreams,
    )


class Assembler(Executable):

    """
    `.Executable` bundled with useful plugins.
    """

    results = Instance(DictObject)
    """
    Attributes set to this property are saved to `.datastore` by
    `.AutoDump` plugin.  Downstream classes *must* rely only on the
    data under this property.  For debugging purpose, use `.dbg` to
    store intermediate variables.
    """

    magics = MagicPlugins
    """
    Plugins that work behind the scene.
    """

    from .plugins import (
        Debug as dbg,
        Logger as logger,
    )

    class figure(Figure):
        """
        `.Figure` with `.SubDataStore`.
        """

        datastore = SubDataStore  # Figure.datastore is Delegate()

    datastore = DirectoryDataStore
    r"""
    This is a "conventional" property in the sense `Assembler` class
    itself is not aware of this property.  However, this is the most
    heavily used property accessed by many sub-`.Executable`\ s and
    `.Plugin`\ s.  Those "users" of `datastore` property expects it to
    be a subclass of `.BaseDataStore`.
    """

    @property
    def nargs(self):
        """
        Number of arguments of the `.run` method accept.

        Same syntax as the one accepted by
        `argparse.ArgumentParser.add_argument`.

        """
        raise NotImplementedError


class Loader(Assembler):
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


class Plotter(Assembler):

    """
    An `.Assembler` subclass specialized for plotting.

    Example
    -------
    ::

      class DensityPlotter(Plotter):
          pass

      class CumulativeDistributionPlotter(Plotter):
          pass

      class MyApp(Computer):
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
