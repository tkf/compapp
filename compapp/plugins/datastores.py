import os

from ..core import Plugin
from ..descriptors import Link, OwnerName, Owner, Required


class BaseDataStore(Plugin):
    pass


def iswritable(directory):
    """
    Check if `directory` is writable.

    >>> iswritable('.')
    True

    >>> os.path.exists('spam')
    False
    >>> iswritable('spam/egg')
    True

    >>> os.access('/', os.W_OK | os.X_OK)
    False
    >>> os.path.exists('/spam')
    False
    >>> iswritable('/spam/egg')
    False

    """
    parent = os.path.realpath(directory)
    cur = os.path.join(parent, '_dummy_')
    while parent != cur:
        if os.path.exists(parent):
            if os.access(parent, os.W_OK | os.X_OK):
                return True
            else:
                return False
        cur, parent = parent, os.path.dirname(parent)


class DirectoryDataStore(BaseDataStore):

    """
    Data-store using a directory.

    Examples
    --------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    >>> mp = MyParametric()
    >>> mp.datastore.dir = 'out'
    >>> mp.datastore.path('file')
    'out/file'

    `.path` creates intermediate directories if required:

    >>> os.listdir('.')
    ['out']

    If a :term:`nested class` uses `DirectoryDataStore`, the path is
    automatically allocated under the `.dir` of the :term:`owner
    class`.

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    ...     class nested(Parametric):
    ...         datastore = DirectoryDataStore
    ...
    >>> mp = MyParametric()
    >>> mp.datastore.dir = 'out'
    >>> mp.nested.datastore.path()
    'out/nested'
    >>> mp.nested.datastore.path('file')
    'out/nested/file'
    >>> mp.nested.datastore.path('dir', 'file')
    'out/nested/dir/file'

    >>> mp.nested.datastore.dir = 'another'
    >>> mp.nested.datastore.path('file')
    'another/file'

    """

    _parent = Link('...datastore')
    _ownername = OwnerName()
    overwrite = True
    clear_before_run = True

    @property
    def dir(self):
        try:
            return self._dir
        except AttributeError:
            pass
        try:
            parentdir = self._parent.dir
            ownername = self._ownername
        except AttributeError:
            return None
        return os.path.join(parentdir, ownername)

    @dir.setter
    def dir(self, value):
        assert isinstance(value, str)
        self._dir = value

    def prepare(self):
        if hasattr(self, '_dir') and not iswritable(self._dir):
            raise RuntimeError("Directory {0} is not writable."
                               .format(self._dir))

    def path(self, *args, **kwds):
        """
        Path relative to the base directory `.dir`.

        Parameters
        ----------
        args : str
          Path relative to `.dir`.
          It will be joined by `os.path.join`.

        Keyword Arguments
        -----------------
        mkdir : bool
           If `True` (default), make the parent directory of returned
           `path` (i.e., ``os.path.dirname(path)``, not the `path`
           itself).

        Returns
        -------
        path : str
           ``os.path.join(self.dir, *args)``

        """
        def makepath(args, mkdir=True):
            path = os.path.join(self.dir, *args)
            dirname = os.path.dirname(path)
            if mkdir and not os.path.isdir(dirname):
                os.makedirs(dirname)
            return path
        return makepath(args, **kwds)


class SubDataStore(DirectoryDataStore):

    """
    Data-store using sub-paths of parent data-store.

    Examples
    --------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    ...     class nested(Parametric):
    ...         datastore = SubDataStore
    ...
    >>> mp = MyParametric()
    >>> mp.datastore.dir = 'out'
    >>> mp.nested.datastore.path()
    'out/nested'
    >>> mp.nested.datastore.path('file')
    'out/nested-file'
    >>> mp.nested.datastore.path('dir', 'file')
    'out/nested-dir/file'
    >>> mp.nested.datastore.path('a', 'b', 'c')
    'out/nested-a/b/c'
    >>> mp.nested.datastore.sep = '.'
    >>> mp.nested.datastore.path('file')
    'out/nested.file'

    Since `DirectoryDataStore` already can be used for datastore using
    sub-directories, this class is specialized for the case using
    files under the directory of parent datastore.  If the
    :term:`owner class` of this datastore uses only a few files, it
    makes sense to not allocate a directory and to use this type of
    datastore.

    """

    # MAYBE: this class should be called ParasiteDataStore?

    dir = None  # null-out the dir parameter
    _parent = Link('...datastore')
    _ownername = OwnerName()
    sep = '-'

    def path(self, *args, **kwds):
        # but how about List/Dict?
        if not args:
            return self._parent.path(self._ownername)
        part0 = self._ownername + self.sep + args[0]
        return self._parent.path(part0, *args[1:], **kwds)


class HashDataStore(DirectoryDataStore):

    """
    Automatically allocated data-store based on hash of parameter.
    """

    basedir = Required(str)
    owner = Owner()
    include_plugin_parameters = False

    def ownerhash(self):
        def not_datastore(key, value):
            pass
        params = self.owner.params(deep=True, include=not_datastore)
        ownerclass = type(self.owner)
        return self.sha1(ownerclass, params)

    def run(self):
        digest = self.ownerhash()
        path = os.path.join(self.basedir, digest[:2], digest[2:])
        os.makedirs(path)
        self.dir = path
