from ..core import DataDescriptor
from ..utils.importer import import_object


class ClassPath(DataDescriptor):

    def __init__(self, default, prefix=None):
        super(ClassPath, self).__init__(default=default)
        self.prefix = prefix

    def verify(self, obj, value, myname=None):
        ret = super(ClassPath, self).verify(obj, value, myname)
        self.getclass(obj)
        return ret

    def getclass(self, obj):
        path = self.get(obj)
        if path.startswith('.'):
            if self.prefix is None:
                raise ValueError('relative import path is specified but no'
                                 ' prefix is defined.')
            path = self.prefix + path
        return import_object(path)


class ClassPlaceholder(DataDescriptor):

    def __init__(self, cpath, **kwds):
        super(ClassPlaceholder, self).__init__(**kwds)
        self.cpath = cpath

    def get(self, obj):
        value = super(ClassPlaceholder, self).get(obj)
        cls = self.cpath.getclass(obj)
        if isinstance(value, cls):
            return value

        newval = cls(value)
        self.__set__(obj, newval)
        return newval


def dynamic_class(path, prefix=None, **kwds):
    """
    Dynamic class loading helper.

    >>> from compapp import Parametric, dynamic_class
    >>> class MyApp(Parametric):
    ...     obj, path = dynamic_class('.ClassA', prefix=__name__, default={})
    ...
    >>> class ClassA:
    ...     def __init__(self, params):
    ...         self.params = params
    ...
    >>> class ClassB(ClassA):
    ...     pass
    ...

    .. hack to make it work in doctest:
       >>> import sys
       >>> mod = sys.modules[__name__]
       >>> mod.ClassA = ClassA
       >>> mod.ClassB = ClassB

    >>> app = MyApp()
    >>> app.obj                                        # doctest: +ELLIPSIS
    <....ClassA ... at 0x...>
    >>> app.obj.params
    {}

    >>> app2 = MyApp(obj={'a': 1}, path='.ClassB')
    >>> app2.obj                                       # doctest: +ELLIPSIS
    <....ClassB ... at 0x...>
    >>> app2.obj.params
    {'a': 1}

    .. undo the hack:
       >>> del mod.ClassA
       >>> del mod.ClassB

    """
    cpath = ClassPath(default=path, prefix=prefix)
    return ClassPlaceholder(cpath, **kwds), cpath
