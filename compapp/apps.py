"""
Application base classes.

.. inheritance-diagram::
   Application
   SimulationApp
   AnalysisApp
   :parts: 1

"""

from .core import Executable
from .plugins import PluginWrapper


class ApplicationPlugins(PluginWrapper):
    from .plugins import (
        AutoDump as autodump,
        RecordVCS as recordvcs,
        RecordTiming as recordtiming,
        DumpParameters as dumpparameters,
    )


class Application(Executable):

    """
    Application base class.

    Everything needed for save/load functions are implemented in
    :attr:`plugin`.  So, all the methods you need to implement are
    :meth:`run` and (optionally) :meth:`upstreams`.

    Examples
    --------

    **Strict attribute.**
    `Application` subclass does not allow setting attribute other than
    its parameter or result (specified by :attr:`result_names`).
    This makes sure that `Application` holds the same data after `run`
    and `load`.  To save intermediate data for debugging for
    interactive use, set it to :attr:`dbg` (instance of `.Debug`).

    >>> class MyApp(Application):
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

    from .plugins import (
        Debug as dbg,
        Figure as figure,
        Logger as logger,
    )
    plugin = ApplicationPlugins

    @classmethod
    def cli(cls, args=None):
        """
        Run Command Line Interface of this class.

        Examples
        --------
        ::

            myapp.py --datastore.dir OUT
            myapp.py --sub.floats[0] 10
            myapp.py --sub.plotters[0].bin 100
            myapp.py parameters.yaml

        If multiple parameter files are given, they will be mixed together
        before giving to the class::

            myapp.py base.yaml extension.yaml

        Data file for nested classes (``:file=`` modifier)::

            myapp.py --simulator:file=param.yaml --plotter:file=plotter.json

        Loading subset of data using JSON pointer::

            myapp.py --simulator:file=param.yaml#/param/simulator

        Literal eval (``:leval=`` modifier)::

            myapp.py --alpha:leval='2**3'

        Regular help::

            myapp.py -h
            myapp.py --help

        Full Help (include full list of parameters)::

            myapp.py -H
            myapp.py --help-all

        """

    @classmethod
    def get_parser(cls):
        pass

    @classmethod
    def from_param(cls, param, require_all=False, filter_param=False):
        """
        Create an instance based on `param` and `execute` it.

        Parameters
        ----------
        param : dict
        require_all : bool
            If true, a `ValueError` is raised if `param` does not have
            all parameters for this and nested `Parametric` classes.
        filter_param : bool
            If true, keys and sub-keys in `param` which is not valid
            to this class are removed.

        Returns
        -------
        self : Application

        """
        self = cls(**param)
        self.execute()
        return self


class SimulationApp(Application):

    """
    `Application` with `.DirectoryDataStore`.
    """

    from .plugins import DirectoryDataStore as datastore


class AnalysisApp(Application):

    """
    `Application` with `.HashDataStore`.
    """

    from .plugins import HashDataStore as datastore
