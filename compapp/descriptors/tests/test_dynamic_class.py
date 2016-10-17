from ...core import Parametric
from .. import Delegate, dynamic_class


class SubparamA(Parametric):
    x = Delegate()


class SubparamB(Parametric):
    x = Delegate()


class DynamicParam(Parametric):
    sub, sub_class = dynamic_class('.SubparamA', __name__)
    x = 1.0


def test_default():
    par = DynamicParam()
    assert isinstance(par.sub, SubparamA)


def test_dynamics():
    par = DynamicParam(sub_class='.SubparamB')
    assert isinstance(par.sub, SubparamB)


def test_link():
    par = DynamicParam()
    assert par.sub.x == 1.0
    par.x = 2.0
    assert par.sub.x == 2.0
