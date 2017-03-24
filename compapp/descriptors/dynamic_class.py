"""
Descriptors for dynamic class loading
=====================================

Implementation details
----------------------

`dynamic_class` works by defining a pair of descriptors for holding
"class path" (`ClassPath`) and the instance of the class
(`ClassPlaceholder`).  Those descriptors make sure that they are
consistent; changing `ClassPath` "sets" the class of the objects at
`ClassPlaceholder` and setting the instance directly at
`ClassPlaceholder` changes `ClassPath`.  Accessing the value at
`ClassPlaceholder` when it is inconsistent with `ClassPath` raises a
`ValueError`.

"""

import sys

from ..core import Unspecified, DataDescriptor, private, Parameter
from ..utils.importer import import_object


class ClassPath(DataDescriptor):

    """
    Class path descriptor that imports specified class on change.
    """

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

    """
    Placeholder for an instance of the class specified by `.ClassPath`.

    The actual instantiation process is delayed until it is accessed
    (i.e., `__get__` method is called).

    """

    def __init__(self, cpath, **kwds):
        super(ClassPlaceholder, self).__init__(**kwds)
        self.cpath = cpath

    def get(self, obj):
        value = super(ClassPlaceholder, self).get(obj)
        cls = self.cpath.getclass(obj)
        if isinstance(value, cls):
            return value
        elif value is Unspecified or isinstance(value, dict):
            pass
        else:
            vname = self.myname(obj)
            pname = self.cpath.myname(obj)
            classpath = self.cpath.get(obj)
            raise ValueError(
                "Trying to get obj.{vname}={value!r} but it does not"
                " match with class path obj.{pname}={classpath}.\n"
                "The class path obj.{pname} might be changed after the"
                " first access of obj.{vname}.\n"
                "Note: obj={obj!r}."
                .format(**locals()))

        newval = cls() if value is Unspecified else cls(value)

        # Set the instantiated newval now.  Calling
        # DataDescriptor.__set__ instead of self.__set__ to avoid
        # resetting ClassPath.
        super(ClassPlaceholder, self).__set__(obj, newval)

        if isinstance(newval, Parameter):
            private(newval).set_context(obj, self.myname(obj, error=True))
        return newval

    def __set__(self, obj, value):
        super(ClassPlaceholder, self).__set__(obj, value)
        if isinstance(value, dict):
            return
        cls = type(value)
        path = sys.modules[cls.__module__].__name__ + '.' + cls.__name__
        self.cpath.__set__(obj, path)


def dynamic_class(path, prefix=None, **kwds):
    """
    Dynamic class loading helper.

    .. hack to make it work in doctest:
       >>> import mock
       >>> __name__ = '{module name}'
       >>> mod = sys.modules[__name__] = mock.Mock()
       >>> mod.__name__ = __name__

    >>> from compapp import Parametric, dynamic_class
    >>> class MyApp(Parametric):
    ...     obj, path = dynamic_class('.ClassA', prefix=__name__, default={})
    ...
    >>> class ClassA(object):
    ...     def __init__(self, params):
    ...         self.params = params
    ...
    >>> class ClassB(ClassA):
    ...     pass
    ...

    .. hack to make it work in doctest:
       >>> mod.ClassA = ClassA
       >>> mod.ClassB = ClassB
       >>> ClassA.__module__ = ClassB.__module__ = __name__

    >>> app = MyApp()
    >>> app.obj                                        # doctest: +ELLIPSIS
    <{module name}.ClassA object at 0x...>
    >>> app.obj.params
    {}

    >>> app2 = MyApp(obj={'a': 1}, path='.ClassB')
    >>> app2.obj                                       # doctest: +ELLIPSIS
    <{module name}.ClassB object at 0x...>
    >>> app2.obj.params
    {'a': 1}

    >>> app3 = MyApp()
    >>> app3.obj = ClassB({})
    >>> app3.path
    '{module name}.ClassB'

    .. undo the hack:
       >>> del sys.modules[__name__]

    """
    if isinstance(path, type):
        path = sys.modules[path.__module__].__name__ + '.' + path.__name__
    cpath = ClassPath(default=path, prefix=prefix)
    return ClassPlaceholder(cpath, **kwds), cpath
