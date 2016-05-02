from ..core import Plugin


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
    ::

      class MyApp(Computer):
          # Note: Computer includes AutoDump by default

          def run(self):
              self.results.alpha = dict(pi='3.14')

    Then ``MyApp({'datastore.dir': 'OUT'}).execute()`` creates a JSON
    file at ``OUT/results.json`` with content ``{'alpha': {'pi':
    3.14}}``.

    """

    result_names = ('results',)
    """
    These attributes of the owner class are dumped.
    """


class DumpParameters(Plugin):

    """
    Dump parameters used for its owner.
    """
    # FIXME: It should be included by default when `HashDataStore` is
    #        used.  How to avoid running it twice (i.e.,
    #        `DumpParameters` explicitly specified and the one called
    #        via `HashDataStore`)?


class RecordVCS(Plugin):

    """
    Record VCS revision automatically.
    """

    vcs = 'git'


class RecordTiming(Plugin):

    """
    Record timing information.
    """

    def pre_run(self):
        pass

    def post_run(self):
        pass
