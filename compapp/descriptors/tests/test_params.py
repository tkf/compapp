from ...core import Parametric
from .. import Dict, List


def test_dict_wo_default():
    class MyApp(Parametric):
        x = Dict()

    assert MyApp.paramnames() == ['x']


def test_list_wo_default():
    class MyApp(Parametric):
        x = List()

    assert MyApp.paramnames() == ['x']
