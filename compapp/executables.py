"""
Executable subclasses.
"""

import inspect

from .base import DictObject
from .core import Executable
from .descriptors import OfType, Choice, Link
from .plugins import PluginWrapper, Figure, \
    SubDataStore, DirectoryDataStore


class MagicPlugins(PluginWrapper):
    from .plugins import (
        MetaStore as meta,
        DumpResults as dumpresults,
        RecordVCS as recordvcs,
        RecordTiming as recordtiming,
        RecordProgramInfo as programinfo,
        RecordSysInfo as sysinfo,
        DumpParameters as dumpparameters,
        AutoUpstreams as autoupstreams,
    )


class Assembler(Executable):

    """
    `.Executable` bundled with useful plugins.
    """

    mode = Choice('run', 'load', 'auto', isparam=False)
    """
    Execution mode.  The mode ``'run'`` and ``'load'`` means to call
    `.run` and `.load`, respectively.  When ``'auto'`` is specified,
    call `.run` if `.is_loadable` returns `True` otherwise call
    `.load`.
    """

    results = OfType(init=DictObject, isparam=False)
    """
    Attributes set to this property are saved to `.datastore` by
    `.DumpResults` plugin.  Downstream classes must rely *only* on the
    data under this property.  For debugging purpose, use `.dbg` to
    store intermediate variables.
    """

    magics = MagicPlugins
    """
    Plugins that work behind the scene.
    """

    from .plugins import (
        Debug as debug,
        Logger as log,
    )

    dbg = Link('.debug.ns')

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

    def should_load(self):
        return (self.mode == 'load' or
                self.mode == 'auto' and self.is_loadable())

    def is_loadable(self):
        """
        |TO BE EXTENDED| Return `True` if `self` is loadable.

        Default implementation calls
        `self.datastore.exists('params.json')
        <.DirectoryDataStore.exists>`.

        """
        return self.datastore.exists('params.json')

    @property
    def argrange(self):
        """
        Number of arguments that the `.run` method accepts.

        >>> class MyComp00(Assembler):
        ...     def run(self):
        ...         pass
        ...
        >>> MyComp00().argrange
        (0, 0)

        >>> class MyComp12(Assembler):
        ...     def run(self, x, y=1):
        ...         pass
        ...
        >>> MyComp12().argrange
        (1, 2)

        >>> class MyComp2i(Assembler):
        ...     def run(self, x, y, *args):
        ...         pass
        ...
        >>> MyComp2i().argrange
        (2, None)

        """
        (args, varargs, _, defaults) = inspect.getargspec(self.run)
        nargs = len(args) - 1
        return (
            nargs - (len(defaults) if defaults else 0),  # min
            None if varargs else nargs,                  # max
        )


class Loader(Assembler):
    """
    :term:`Data source` loaded from disk.
    """

    class magics(MagicPlugins):
        dumpresults = None  # null-out
    """
    Since no heavy computations are needed, `.DumpResults` plugin is not
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
