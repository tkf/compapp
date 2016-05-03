import unittest

from ..core import Parametric


class MyParametric(Parametric):
    i = 1
    x = 2.0

    class nested(Parametric):
        a = 100
        b = 200


class TestMixObject(unittest.TestCase):

    class AutoMixed(MyParametric):
        class nested(object):
            a = -1

    def test_default_value(self):
        par = self.AutoMixed()
        assert isinstance(par.nested, MyParametric.nested)
        assert par.nested.a == -1
        assert par.nested.params() == {'a': -1, 'b': 200}

    def test_custom_value(self):
        par = self.AutoMixed(nested=dict(a=-2))
        assert isinstance(par.nested, MyParametric.nested)
        assert par.nested.a == -2
        assert par.nested.params() == {'a': -2, 'b': 200}


class TestMixClassObj(TestMixObject):

    class AutoMixed(MyParametric):
        class nested:
            a = -1


def test_assembler_init():
    from ..executables import Assembler
    from ..plugins import PluginWrapper, DumpResults
    excbl = Assembler()
    assert isinstance(excbl.magics, PluginWrapper)
    assert isinstance(excbl.magics.dumpresults, DumpResults)
