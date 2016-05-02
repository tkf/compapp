import os

from ..core import Plugin
from ..descriptors import Link, Delegate, Owner, OwnerInfo, Required, Or


class BaseDataStore(Plugin):
    pass


class DirectoryDataStore(BaseDataStore):

    """
    Data-store using a directory.

    Examples
    --------

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    >>> mp = MyParametric({'datastore.dir': 'out'})
    >>> mp.path('file')
    'out/file'

    If a :term:`nested class` uses `DirectoryDataStore`, the path is
    automatically allocated under the `.dir` of the :term:`owner
    class`.

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    ...     class nested(Parametric):
    ...         datastore = DirectoryDataStore
    ...
    >>> mp = MyParametric({'datastore.dir': 'out'})
    >>> mp.nested.datastore.path()
    'out/nested'
    >>> mp.nested.datastore.path('file')
    'out/nested/file'
    >>> mp.nested.datastore.path('dir', 'file')
    'out/nested/dir/file'

    """

    def __dir_adapter(self, value):
        # In the above example:
        #    value == 'out'
        #    self.ownerinfo.name == 'nested'
        return os.path.join(self.ownerinfo.name, value)

    dir = Or(Delegate(adapter=__dir_adapter), Required(str))
    ownerinfo = OwnerInfo()
    overwrite = True
    clear_before_run = True

    def prepare(self):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)

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

    >>> class MyParametric(Parametric):
    ...     datastore = DirectoryDataStore
    ...
    ...     class nested(Parametric):
    ...         datastore = SubDataStore
    ...
    >>> mp = MyParametric({'datastore.dir': 'out'})
    >>> mp.nested.datastore.path()
    'out/nested'
    >>> mp.nested.datastore.path('file')
    'out/nested-file'
    >>> mp.nested.datastore.path('dir', 'file')
    'out/nested-dir/file'
    >>> mp.nested.datastore.path('a', 'b', 'c')
    'out/nested-a/b/c'
    >>> mp.nested.sep = '.'
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
    datastore = Link('...datastore')
    ownerinfo = OwnerInfo()
    sep = '-'

    def path(self, *args, **kwds):
        # but how about List/Dict?
        if not args:
            self.datastore.path(self.name)
        part0 = self.name + self.sep + args[0]
        return self.datastore.path(part0, *args[1:], **kwds)


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
