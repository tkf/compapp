from collections import OrderedDict

from ..apps import Computer
from ..descriptors.dynamic_class import dynamic_class
from ..setters import rec_setattrs


class MyApp(Computer):
    dynamic, classpath = dynamic_class('.ClassA', prefix=__name__, default={})


class ClassA(object):
    def __init__(self, params):
        self.params = params


class ClassB(ClassA):
    pass


def test_subs_dynamic_class():
    data = OrderedDict([
        ('dynamic', dict(x=1)),
        ('classpath', '.ClassB'),
    ])
    app = MyApp()
    rec_setattrs(app, data)
    assert isinstance(app.dynamic, ClassB)
    assert app.dynamic.x == 1
