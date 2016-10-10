import pytest

from ...core import Parametric
from .. import Dict, List, Or, Link


def test_dict_with_default():
    class MyApp(Parametric):
        x = Dict(default=dict(y=dict(z=1)))

    assert MyApp.paramnames() == ['x']
    x0 = MyApp.defaultparams()['x']
    x1 = MyApp().params()['x']
    assert x0 is not x1
    assert x0['y'] is not x1['y']
    assert x0 == x1


def test_dict_wo_default():
    class MyApp(Parametric):
        x = Dict()

    assert MyApp.paramnames() == ['x']


def test_list_wo_default():
    class MyApp(Parametric):
        x = List()

    assert MyApp.paramnames() == ['x']


def test_or_default():
    class MyApp(Parametric):
        x = Or(List(),
               Dict(default=dict(y=dict(z=1))))

    assert MyApp.paramnames() == ['x']
    x0 = MyApp.defaultparams()['x']
    x1 = MyApp().params()['x']
    assert x0 is not x1
    assert x0['y'] is not x1['y']
    assert x0 == x1


@pytest.mark.skip(reason="spec not decided")
def test_link_default():
    class MyApp(Parametric):
        x = 1

        class sub(Parametric):
            x = Link('..x')

    assert sorted(MyApp.paramnames()) == ['sub', 'x']
    defaultparams = MyApp.defaultparams(nested=True)
    params = MyApp().params(nested=True)
    assert defaultparams == params == {'x': 1, 'sub': {'x': 1}}
