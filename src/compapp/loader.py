import os
import json

from .plugins.metastore import MetaStore
from .utils.importer import import_object


def _meta_path(path):
    path = os.path.abspath(path)
    basename = os.path.basename(path)
    if basename == MetaStore.metafile:
        return path
    elif basename == 'params.json':
        return os.path.join(os.path.dirname(path), MetaStore.metafile)
    elif os.path.isdir(path):
        return os.path.join(path, MetaStore.metafile)
    else:
        raise RuntimeError("Meta file not found at: {}".format(path))


def load(path):
    """
    Load result saved at `path`.

    `path` can be a path to a datastore directory, a path to a
    params.json file, or a path to a meta.json file.

    Examples
    --------
    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> from compapp import Computer, load
    >>> class MyApp(Computer):
    ...     x = 1
    ...     def run(self):
    ...         self.results.y = self.x ** 2

    .. a hack to make it work in doctest:
       >>> import sys
       >>> sys.modules[__name__].MyApp = MyApp

    >>> app = MyApp()
    >>> app.datastore.dir = 'out'
    >>> app.execute()
    >>> assert load('out').results == app.results
    >>> assert load('out/meta.json').results == app.results
    >>> assert load('out/params.json').results == app.results

    .. rewind the hack:
       >>> del sys.modules[__name__].MyApp

    """
    metapath = _meta_path(path)
    with open(metapath) as file:
        meta = json.load(file)
    classname = meta['programinfo']['class']
    module = meta['programinfo']['module']
    cls = import_object(module + '.' + classname)
    app = cls()
    app.mode = 'load'
    app.datastore.dir = os.path.dirname(metapath)
    app.execute()
    return app
