"""
Application base classes.

.. inheritance-diagram::
   Computer
   Memoizer
   :parts: 1

"""

from .executables import Assembler


class Computer(Assembler):

    r"""
    Application base class.

    Everything needed for save/load functions are implemented by
    plugins (see: :attr:`.magics`).  Only the method :meth:`run` is
    needed to be implemented most of the cases.

    """

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
        self : Computer

        """
        self = cls(**param)
        self.execute()
        return self


class Memoizer(Computer):

    """
    `Computer` with `.HashDataStore`.
    """

    from .plugins import HashDataStore as datastore
