from ..core import Parametric, itervars
from ..descriptors import Link


class ParWithMissingLink(Parametric):
    sub = Parametric
    link = Link('.sub.x')


def test_missing_link():
    par = ParWithMissingLink()
    vars0 = dict(itervars(par))
    assert 'link' not in vars0
    par.sub.x = 1
    vars1 = dict(itervars(par))
    assert 'link' in vars1
