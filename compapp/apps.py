"""
Application base classes.

.. inheritance-diagram::
   Computer
   Memoizer
   :parts: 1

"""

import sys

from .descriptors import Choice
from .executables import Assembler
from .parser import make_parser, process_assignment_options, parseargs


class Computer(Assembler):

    r"""
    Application base class.

    Everything needed for save/load functions are implemented by
    plugins (see: :attr:`.magics`).  Only the method :meth:`run` is
    needed to be implemented most of the cases.

    """

    def cli(self, args=None):
        """
        Run Command Line Interface of this class.

        Examples
        --------
        ::

            myapp.py --datastore.dir OUT
            myapp.py --sub.floats[0] 10
            myapp.py --sub.plotters[0].bin 100
            myapp.py --params parameters.yaml

        If multiple parameter files are given, they will be mixed together
        before giving to the class::

            myapp.py --params base.yaml extension.yaml

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
        parser = self.get_parser()
        parser.add_argument('--params', nargs='+', default=[])
        ns, opts, poss = parseargs(parser, args)
        if ns.help_full:
            raise NotImplementedError
            sys.exit()
        if ns.params:
            raise NotImplementedError
        process_assignment_options(self, opts)
        self.execute(*poss)
        return self

    @classmethod
    def get_parser(cls):
        return make_parser(cls.__doc__)

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

    Examples
    --------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> class UpStream1(Memoizer):
    ...
    ...     parameter = 1
    ...
    ...     def run(self):
    ...         self.results.data = 'result of intense computation'
    ...         self.results.name = type(self).__name__
    ...         self.isrun = True
    ...
    ...     def load(self):
    ...         self.isrun = False
    ...
    >>> class UpStream2(UpStream1):
    ...     pass
    ...
    >>> class DownStream(UpStream1):
    ...     up1 = UpStream1
    ...     up2 = UpStream2
    ...
    ...     def run(self):
    ...         self.up1.execute()
    ...         self.up2.execute()
    ...         super(DownStream, self).run()
    ...         self.results.sum = (self.up1.results.data +
    ...                             self.up2.results.data)
    ...
    >>> up1 = UpStream1()
    >>> up1.execute()
    >>> assert up1.isrun
    >>> up1 = UpStream1()
    >>> up1.execute()
    >>> assert not up1.isrun
    >>> down = DownStream()
    >>> down.execute()
    >>> assert not down.up1.isrun
    >>> assert down.up2.isrun
    >>> assert down.isrun
    >>> down.up1.results.data == 'result of intense computation'
    True

    """

    from .plugins import HashDataStore as datastore

    mode = Choice('auto', 'run', 'load', isparam=False)
