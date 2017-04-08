from ...core import Parametric
from .. import Dict, List, Or, Link


def test_dict_wo_default():
    class MyApp(Parametric):
        x = Dict()

    assert MyApp.paramnames() == ['x']


def test_list_wo_default():
    class MyApp(Parametric):
        x = List()

    assert MyApp.paramnames() == ['x']


class TestDictWithDefault(object):

    class MyApp(Parametric):
        _desired = dict(y=dict(z=1))
        x = Dict(default=_desired)

    def test(self):
        MyApp = self.MyApp
        desired = MyApp._desired
        assert MyApp.paramnames() == ['x']
        x0 = MyApp.defaultparams()['x']
        x1 = MyApp().params()['x']
        assert x0 is not x1
        assert x0['y'] is not x1['y']
        assert x0 == x1 == desired


class TestOrDefault(TestDictWithDefault):

    class MyApp(Parametric):
        _desired = dict(y=dict(z=1))
        x = Or(List(), Dict(default=_desired))


def test_link_default():
    class MyApp(Parametric):
        x = 1

        class sub(Parametric):
            x = Link('..x', isparam=True)

    assert sorted(MyApp.paramnames()) == ['sub', 'x']
    defaultparams = MyApp.defaultparams(nested=True)
    params = MyApp().params(nested=True)
    assert params == {'x': 1, 'sub': {'x': 1}}
    assert defaultparams == {'x': 1, 'sub': {'x': 1}}
