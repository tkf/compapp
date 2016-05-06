from . import utils
from ..apps import Computer
from ..base import deepmixdicts
from ..descriptors import OfType, Dict, List, Or


class NoOp(Computer):
    class sub(Computer):
        class sub(Computer):
            class sub(Computer):
                pass


def test_nested_empty_computer():
    app = NoOp()
    app.execute()


class TestCLISimpleTypes(utils.DataChecker):

    def check(self, args, nondefaults):
        desired = dict(self.appclass.defaultparams(), **nondefaults)
        app = self.appclass()
        app.cli(args)
        actual = app.params()
        assert actual == desired

    class appclass(Computer):
        i = 1
        x = 1.0
        z = 1.0j
        s = 'a'
        b = True

    data = [
        ([], {}),
        (['--i=2'], dict(i=2)),
        (['--i', '2'], dict(i=2)),
        (['--x=2.0'], dict(x=2.0)),
        (['--x', '2.0'], dict(x=2.0)),
        (['--x=2'], dict(x=2.0)),
        (['--x', '2'], dict(x=2.0)),
        (['--z=1+2j'], dict(z=1+2j)),
        (['--z', '1+2j'], dict(z=1+2j)),
        (['--z:leval=1+2j'], dict(z=1+2j)),
        (['--z:leval', '1+2j'], dict(z=1+2j)),
        (['--s=A'], dict(s='A')),
        (['--s', 'A'], dict(s='A')),
        (['--s:leval="A"'], dict(s='A')),
        (['--s:leval', '"A"'], dict(s='A')),
        (['--b=true'], dict(b=True)),
        (['--b', 'true'], dict(b=True)),
        (['--b=yes'], dict(b=True)),
        (['--b', 'yes'], dict(b=True)),
        (['--b=1'], dict(b=True)),
        (['--b', '1'], dict(b=True)),
        (['--b=false'], dict(b=False)),
        (['--b', 'false'], dict(b=False)),
        (['--b=no'], dict(b=False)),
        (['--b', 'no'], dict(b=False)),
        (['--b=0'], dict(b=False)),
        (['--b', '0'], dict(b=False)),
        (['--b:leval=False'], dict(b=False)),
        (['--b:leval', 'False'], dict(b=False)),
    ]


class TestCLISimpleOfType(TestCLISimpleTypes):

    class appclass(Computer):
        i = OfType(int, default=1)
        x = OfType(float, default=1.0)
        z = OfType(complex, default=1.0j)
        s = OfType(str, default='a')
        b = OfType(bool, default=True)


class TestCLICompositeTraits(TestCLISimpleTypes):
    class appclass(Computer):
        anysimple = Or(OfType(int),
                       OfType(float),
                       OfType(complex),
                       OfType(bool),  # must be before str
                       OfType(str),
                       default=1)

    data = [
        ([], {}),
        (['--anysimple=2'], dict(anysimple=2)),
        (['--anysimple=2.0'], dict(anysimple=2.0)),
        (['--anysimple=2.0j'], dict(anysimple=2.0j)),
        (['--anysimple=a'], dict(anysimple='a')),
        (['--anysimple=yes'], dict(anysimple=True)),
    ]


class TestCLINestedSimpleTypes(utils.DataChecker):

    def check(self, args, nondefaults):
        desired = deepmixdicts(self.appclass.defaultparams(nested=True),
                               nondefaults)
        app = self.appclass()
        app.cli(args)
        actual = app.params(nested=True)
        assert actual == desired

    class appclass(Computer):
        i = 1

        class sub(Computer):
            j = 2

            class sub(Computer):
                k = 3

                class sub(Computer):
                    l = 4

    data = [
        ([], {}),
        (['--i', '10'], dict(i=10)),
        (['--sub.j', '10'], dict(sub=dict(j=10))),
        (['--sub.sub.k', '10'], dict(sub=dict(sub=dict(k=10)))),
        (['--sub.sub.sub.l', '10'], dict(sub=dict(sub=dict(sub=dict(l=10))))),
    ]


class TestCLISetItem(TestCLINestedSimpleTypes):

    class appclass(Computer):
        strs = List(str, default=['a', 'b', 'c'])
        dict = Dict(str, str, default={})
        # FIXME: "default=" should not be used here; use "init=" for
        # the same reason why "init=" is used in Logger plugin.

    data = [
        ([], {}),
        (['--strs[1]=B'], dict(strs=['a', 'B', 'c'])),
        (['--dict["a"]=b'], dict(dict=dict(a='b'))),
    ]


def test_file_modifier_for_level1_par(tmpdir):
    class MyApp(Computer):
        class sub(Computer):
            i = 1
            j = 2

    paramfile = tmpdir.join('param.json')
    paramfile.write('{"j": 3}')

    app = MyApp()
    app.cli(['--sub:file', paramfile.strpath])
    assert app.sub.params() == dict(i=1, j=3)


def test_file_modifier_for_level2_par(tmpdir):
    class MyApp(Computer):
        class sub(Computer):
            class sub(Computer):
                i = 1
                j = 2

    paramfile = tmpdir.join('param.json')
    paramfile.write('{"j": 3}')

    app = MyApp()
    app.cli(['--sub.sub:file', paramfile.strpath])
    assert app.sub.sub.params() == dict(i=1, j=3)


def test_file_modifier_for_level1_dict(tmpdir):
    class MyApp(Computer):
        d = Dict(default=dict(i=1, j=2))

    paramfile = tmpdir.join('param.json')
    paramfile.write('{"j": 3}')

    app = MyApp()
    app.cli(['--d:file', paramfile.strpath])
    assert app.params() == dict(d=dict(i=1, j=3))


def test_file_modifier_for_level2_dict(tmpdir):
    class MyApp(Computer):
        class sub(Computer):
            d = Dict(default=dict(i=1, j=2))

    paramfile = tmpdir.join('param.json')
    paramfile.write('{"j": 3}')

    app = MyApp()
    app.cli(['--sub.d:file', paramfile.strpath])
    assert app.sub.params() == dict(d=dict(i=1, j=3))
