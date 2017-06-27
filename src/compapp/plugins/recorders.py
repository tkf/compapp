import itertools
import json
import os
import sys

from ..base import MultiException
from ..core import basic_types, private
from ..interface import Plugin
from ..setters import rec_setattrs
from .misc import real_owner


class DumpResults(Plugin):

    """
    Automatically save owner's results.

    Supported back-ends:

    - `json`
      for `dict`, `list` or `tuple`
    - `numpy.savez`
      for `numpy.ndarray`
    - :ref:`pandas.HDFStore <pandas:io.hdf5>`
      for pandas object

    Example
    -------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> import numpy
    >>> import pandas
    >>> from compapp.apps import Computer

    Examples below use an app class derived from `.Computer` since it
    is bundled with the `DumpResults` plugin:

    >>> Computer.magics.dumpresults
    <class 'compapp.plugins.recorders.DumpResults'>

    >>> class MyApp(Computer):
    ...
    ...     def run(self):
    ...         self.results.int = 0
    ...         self.results.float = 1.0
    ...         self.results.list = [2, 3, 4]
    ...         self.results.tuple = (5, 6, 7)
    ...         self.results.array = numpy.arange(8)
    ...         self.results.df = pandas.DataFrame({'col': [9, 10, 11]})
    ...         self.isrun = True
    ...     isrun = False
    ...
    >>> app = MyApp()
    >>> app.datastore.dir = 'out'
    >>> os.path.exists(app.datastore.dir)
    False
    >>> app.execute()
    >>> app.isrun
    True
    >>> os.path.exists(app.datastore.dir)
    True

    The results of the above "simulation" is saved in
    :file:`results.*` under ``app.datastore.dir``:

    >>> from glob import glob
    >>> sorted(glob(app.datastore.path('results.*')))
    ['out/results.hdf5', 'out/results.json', 'out/results.npz']

    Now let's load these results.

    >>> app2 = MyApp()
    >>> app2.mode = 'load'
    >>> app2.datastore.dir = 'out'
    >>> app2.execute()
    >>> app2.isrun
    False
    >>> sorted(app2.results)
    ['array', 'df', 'float', 'int', 'list', 'tuple']
    >>> app2.results.list
    [2, 3, 4]
    >>> app2.results.array
    array([0, 1, 2, 3, 4, 5, 6, 7])
    >>> app2.results.df
       col
    0    9
    1   10
    2   11

    Note that simple Python types are saved as JSON.  Thus, some type
    information is stripped off after reloading:

    >>> app2.results.tuple
    [5, 6, 7]

    """

    result_names = ('results',)
    """
    These attributes of the owner class are dumped.
    """

    def pre_run(self):
        self.defer()(self._save)

    def save(self):
        self.defer.call()

    def _save(self):
        """
        Actual saving logic to be called from `.save` via `.defer`.

        The saving logic is not implemented directly in `.save` method
        since the results have to be saved even though some error has
        been occurred during computation in owner's `run` method.
        This `._save` method is guaranteed to be called since it is
        recorded in `.defer`.

        """
        self._wait_bg()
        self.save_now()

    def save_now(self):
        """
        Save results to disk immediately.
        """
        owner = private(self).owner
        if not owner.datastore.exists():
            return
        with MultiException.recorder() as mexc:
            for name in self.result_names:
                with mexc.record():
                    mexc.errors.extend(self.save_results(owner, name))

    @classmethod
    def save_results(cls, owner, name):
        results = getattr(owner, name)
        numpy = sys.modules.get('numpy', None)
        pandas = sys.modules.get('pandas', None)

        datamap = {}
        for key, value in results().items():
            if isinstance(value, basic_types):
                ext = 'json'
            elif numpy and isinstance(value, numpy.ndarray):
                ext = 'npz'
            elif pandas and isinstance(value,
                                       pandas.core.generic.PandasObject):
                ext = 'hdf5'
            else:
                yield ValueError("Unsupported type of results: "
                                 "{0} = {1!r}".format(key, value))
                continue
            datamap.setdefault(ext, {})[key] = value

        basepath = owner.datastore.path(name + '.')
        for ext, data in datamap.items():
            try:
                getattr(cls, 'save_results_' + ext)(data, basepath + ext)
            except Exception as err:
                yield err

    @staticmethod
    def save_results_json(data, path):
        with open(path, 'w') as file:
            json.dump(data, file)

    @staticmethod
    def save_results_npz(data, path):
        import numpy
        numpy.savez(path, **data)

    @staticmethod
    def save_results_hdf5(data, path):
        import pandas
        with pandas.HDFStore(path) as store:
            for key, value in data.items():
                store[key] = value
    # http://pandas.pydata.org/pandas-docs/stable/io.html#hdf5-pytables

    def load(self):
        owner = private(self).owner
        iters = []
        for name in self.result_names:
            results = getattr(owner, name)

            for ext in ['json', 'npz', 'hdf5']:
                path = owner.datastore.path(name + '.' + ext, mkdir=False)
                if os.path.exists(path):
                    iters.append(getattr(self, 'load_results_' + ext)(path))

            for key, value in itertools.chain(*iters):
                setattr(results, key, value)

    @staticmethod
    def load_results_json(path):
        with open(path) as file:
            obj = json.load(file)
        return obj.items()

    @staticmethod
    def load_results_npz(path):
        import numpy
        npz = numpy.load(path)
        try:
            for key in npz.files:
                yield key, npz[key]
        finally:
            npz.close()

    @staticmethod
    def load_results_hdf5(path):
        import pandas
        with pandas.HDFStore(path, 'r') as store:
            for key in store.keys():
                yield key.lstrip('/'), store[key]
    # http://pandas.pydata.org/pandas-docs/stable/io.html#hdf5-pytables

    def save_maybe(self):
        """
        Save results in a background thread, if the thread is not busy.
        """
        if not private(self).owner.datastore.exists():
            return
        if not hasattr(self, '_bg_pool'):
            from multiprocessing.dummy import Pool
            self._bg_pool = Pool(1)
        if not hasattr(self, '_bg_result') or \
                self._bg_result.ready() and self._bg_result.successful():
            self._bg_result = self._bg_pool.apply_async(self.save_now)

    def _wait_bg(self):
        if not private(self).owner.datastore.exists():
            return
        if hasattr(self, '_bg_result'):
            try:
                self._bg_result.get()
            finally:
                self._bg_pool.close()
                self._bg_pool.join()


class DumpParameters(Plugin):

    """
    Dump parameters used for its owner.

    Example
    -------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> from compapp.core import Parametric
    >>> from compapp.apps import Computer

    Examples below use an app class derived from `.Computer` since it
    is bundled with the `DumpResults` plugin:

    >>> Computer.magics.dumpparameters
    <class 'compapp.plugins.recorders.DumpParameters'>

    >>> class MyApp(Computer):
    ...     i = 0
    ...     x = 1.0
    ...     class nested(Parametric):
    ...         i = 10
    ...         x = 11.0
    ...
    >>> app = MyApp()
    >>> app.datastore.dir = 'out'
    >>> app.i = -1
    >>> app.execute()

    The parameters are dumped automatically to ``out/params.json``:

    >>> app.datastore.path('params.json')
    'out/params.json'
    >>> os.path.exists('out/params.json')
    True

    Running the app using `mode='load' <Assembler.mode>` automatically
    loads the parameters:

    >>> app2 = MyApp()
    >>> app2.mode = 'load'
    >>> app2.datastore.dir = 'out'
    >>> app2.execute()
    >>> app2.i
    -1

    """
    # FIXME: It should be included by default when `HashDataStore` is
    #        used.  How to avoid running it twice (i.e.,
    #        `DumpParameters` explicitly specified and the one called
    #        via `HashDataStore`)?

    def _verified_owner(self):
        prv = private(self)
        root = prv.getroot()
        owner = real_owner(self)
        if owner is root and owner.datastore.dir:
            return owner

    def pre_run(self):
        owner = self._verified_owner()
        if owner is None:
            return
        with open(owner.datastore.path('params.json'), 'w') as file:
            json.dump(owner.params(nested=True), file)

    def prepare(self):
        owner = self._verified_owner()
        if owner is None:
            return
        if not owner.should_load():
            return
        with open(owner.datastore.path('params.json')) as file:
            data = json.load(file)
        rec_setattrs(owner, data)
