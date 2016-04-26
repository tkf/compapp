"""
Executable subclasses.

.. glossary::

   data source

     Executable classes *not* requiring any other resources other than
     the parameters are called the *data source*.  Data source classes
     provided in this module are:

     .. autosummary::

        Simulator
        DataLoader

   data sink

     Executable classes requiring other resource are called the *data
     sink*.  Data sink classes provided in this module are:

     .. autosummary::

        Analyzer
        Plotter

"""


from .core import Executable


class Simulator(Executable):

    """
    Run computations solely depending on parameters.
    """

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


class Analyzer(Executable):

    """
    Run computations depending on data from other :term:`data source`.
    """

    def execute(self, data, **kwds):
        super(Analyzer, self).execute(data, **kwds)

    def run(self, data):
        """
        |TO BE EXTENDED| Do the actual analysis of `data`.
        """


class Plotter(Analyzer):
    """
    An `.Analyzer` subclass specialized for plotting.
    """
