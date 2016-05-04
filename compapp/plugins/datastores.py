import hashlib
import json
import os

from ..core import private, Plugin
from ..descriptors import Link, OwnerName


class BaseDataStore(Plugin):
    pass


def iswritable(directory):
    """
    Check if `directory` is writable.

    Examples
    --------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

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
        if parentdir is None:
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

    def exists(self, *path):
        return self.dir and os.path.exists(self.path(*path, mkdir=False))


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


def hexdigest(jsonable):
    """
    Calculate hex digest of a `jsonable` object.

    >>> hexdigest({'a': 1, 'b': 2, 'c': 3})
    'e20096b15530bd66a35a7332619f6666e2322070'

    """
    string = json.dumps(jsonable, sort_keys=True).encode()
    return hashlib.sha1(string).hexdigest()


class HashDataStore(DirectoryDataStore):

    """
    Automatically allocated data-store based on hash of parameter.

    Examples
    --------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> from compapp.core import Parametric
    >>> class MyParametric(Parametric):
    ...     datastore = HashDataStore
    ...     a = 1
    ...
    >>> mp = MyParametric()
    >>> mp.datastore.prepare()
    >>> mp.datastore.dir
    'Data/memo/be/a393597a3c5518cad18a4c96c08d038de3f00a'
    >>> mp.a = 2
    >>> mp.datastore.prepare()
    >>> mp.datastore.dir
    'Data/memo/a2/722afcdc53688843b61b8d71329fabab16b6ae'
    >>> mp.datastore.basedir = '.'
    >>> mp.datastore.prepare()
    >>> mp.datastore.dir
    './a2/722afcdc53688843b61b8d71329fabab16b6ae'

    """

    basedir = os.path.join('Data', 'memo')

    def ownerhash(self):
        owner = private(self).owner
        params = owner.params(nested=True)
        del params['datastore']
        cls = type(owner)
        name = cls.__module__ + '.' + cls.__name__
        return hexdigest([name, params])

    def prepare(self):
        digest = self.ownerhash()
        self.dir = os.path.join(self.basedir, digest[:2], digest[2:])
