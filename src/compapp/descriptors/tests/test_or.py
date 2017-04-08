from ...core import Parametric
from .. import Or, OfType, Delegate


class ParOrDelegate(Parametric):
    attr = 1

    class nested(Parametric):
        attr = Or(OfType(int), Delegate())


def test_key_propagation():
    d = ParOrDelegate.nested.attr
    assert d.key is d.traits[0].key is d.traits[1].key


def test_myname_propagation():
    d = ParOrDelegate.nested.attr
    assert d.myname is d.traits[0].myname is d.traits[1].myname


def test_propagated_myname():
    par = ParOrDelegate()
    assert (
        ParOrDelegate.nested.attr.myname(par.nested),
        ParOrDelegate.nested.attr.traits[0].myname(par.nested),
        ParOrDelegate.nested.attr.traits[1].myname(par.nested),
    ) == ('attr',) * 3


def test_function():
    par = ParOrDelegate()
    assert par.nested.attr == 1
    par.attr = 2
    assert par.nested.attr == 2
    par.nested.attr = 3
    assert par.nested.attr == 3
    assert par.attr == 2
