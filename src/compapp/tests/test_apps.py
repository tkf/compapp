import copy
import pickle
import pytest

from ..apps import Computer
from ..base import deepmixdicts
from ..descriptors import OfType, Dict, List, Or, Required, Choice
from ..plugins.misc import _loglevel


@pytest.fixture
def paramfile_j3(request, tmpdir):
    if request.param == 'json':
        paramfile = tmpdir.join('param.json')
        paramfile.write('{"j": 3}')
    elif request.param == 'yaml':
        paramfile = tmpdir.join('param.yaml')
        paramfile.write('j: 3')
    elif request.param == 'pickle':
        paramfile = tmpdir.join('param.pickle')
        with paramfile.open(mode='wb') as file:
            pickle.dump({'j': 3}, file)
    return paramfile
# https://pytest.org/latest/example/parametrize.html#deferring-the-setup-of-parametrized-resources


def pytest_generate_tests(metafunc):
    if 'paramfile_j3' in metafunc.fixturenames:
        metafunc.parametrize('paramfile_j3',
                             ['json', 'yaml', 'pickle'],
                             indirect=True)


class NoOp(Computer):
    class sub(Computer):
        class sub(Computer):
            class sub(Computer):
                pass


def test_nested_empty_computer():
    app = NoOp()
    app.execute()


class SampleCLISimpleTypes(Computer):
    i = 1
    x = 1.0
    z = 1.0j
    s = 'a'
    b = True


class SampleCLISimpleOfType(Computer):
    i = OfType(int, default=1)
    x = OfType(float, default=1.0)
    z = OfType(complex, default=1.0j)
    s = OfType(str, default='a')
    b = OfType(bool, default=True)


@pytest.mark.parametrize(
    "args, nondefaults", [
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
    ])
@pytest.mark.parametrize("appclass", [
    SampleCLISimpleTypes,
    SampleCLISimpleOfType,
])
def test_cli_simple(args, nondefaults, appclass):
    desired = dict(appclass.defaultparams(), **nondefaults)
    app = appclass()
    app.cli(args)
    actual = app.params()
    assert actual == desired


class SampleCLIWithRequired(Computer):
    required = Required(int)


@pytest.mark.parametrize(
    "args, nondefaults", [
        ([], {}),
        (['--required=1'], dict(required=1)),
    ])
def test_cli_with_required(args, nondefaults):
    test_cli_simple(args, nondefaults, SampleCLIWithRequired)


class SampleCLIMicTraits(Computer):
    choice = Choice(1.0, 2, "3", True)
    choice_or_int = Or(Choice("a", "b", "c"), OfType(int))
    loglevel = _loglevel()


@pytest.mark.parametrize(
    "args, nondefaults", [
        ([], {}),
        (['--choice=1'], dict(choice=1.0)),
        (['--choice=2'], dict(choice=2)),
        (['--choice=3'], dict(choice="3")),
        (['--choice=yes'], dict(choice=True)),
        (['--choice_or_int=a'], dict(choice_or_int='a')),
        (['--choice_or_int=1'], dict(choice_or_int=1)),
        (['--loglevel=debug'], dict(loglevel='debug')),
    ])
def test_cli_misc_traits(args, nondefaults):
    test_cli_simple(args, nondefaults, SampleCLIMicTraits)


class SampleCLICompositeTraits(Computer):
    anysimple = Or(OfType(int),
                   OfType(float),
                   OfType(complex),
                   OfType(bool),  # must be before str
                   OfType(str),
                   default=1)


@pytest.mark.parametrize(
    "args, nondefaults", [
        ([], {}),
        (['--anysimple=2'], dict(anysimple=2)),
        (['--anysimple=2.0'], dict(anysimple=2.0)),
        (['--anysimple=2.0j'], dict(anysimple=2.0j)),
        (['--anysimple=a'], dict(anysimple='a')),
        (['--anysimple=yes'], dict(anysimple=True)),
    ])
def test_cli_composite_traits(args, nondefaults):
    test_cli_simple(args, nondefaults, SampleCLICompositeTraits)


class SampleCLINestedSimpleTypes(Computer):
    i = 1

    class sub(Computer):
        j = 2

        class sub(Computer):
            k = 3

            class sub(Computer):
                l = 4


@pytest.mark.parametrize(
    "args, nondefaults", [
        ([], {}),
        (['--i', '10'], dict(i=10)),
        (['--sub.j', '10'], dict(sub=dict(j=10))),
        (['--sub.sub.k', '10'], dict(sub=dict(sub=dict(k=10)))),
        (['--sub.sub.sub.l', '10'], dict(sub=dict(sub=dict(sub=dict(l=10))))),
    ])
def test_cli_nested_simple_types(args, nondefaults,
                                 appclass=SampleCLINestedSimpleTypes):
    desired = deepmixdicts(appclass.defaultparams(nested=True),
                           nondefaults)
    app = appclass()
    app.cli(args)
    actual = app.params(nested=True)
    assert actual == desired


class SampleCLISetItem(Computer):
    strs = List(str, default=['a', 'b', 'c'])
    dict = Dict(str, str, default={})


@pytest.mark.parametrize(
    "args, nondefaults", [
        ([], {}),
        (['--strs[1]=B'], dict(strs=['a', 'B', 'c'])),
        (['--dict["a"]=b'], dict(dict=dict(a='b'))),
    ])
def test_cli_set_item(args, nondefaults):
    test_cli_nested_simple_types(args, nondefaults, SampleCLISetItem)


def test_cli_log_level_propagated():
    app = SampleCLINestedSimpleTypes()
    app.cli(['--log.level=debug'])
    assert (
        app.log.level,
        app.sub.log.level,
        app.sub.sub.log.level,
        app.sub.sub.sub.log.level,
    ) == ('debug',) * 4


def test_cli_log_level_blocked_propagation():
    app = SampleCLINestedSimpleTypes()
    app.cli(['--log.level=debug', '--sub.sub.log.level=critical'])
    assert (
        app.log.level,
        app.sub.log.level,
        app.sub.sub.log.level,
        app.sub.sub.sub.log.level,
    ) == ('debug', 'debug', 'critical', 'critical')


def test_file_modifier_for_level1_par(paramfile_j3):
    class MyApp(Computer):
        class sub(Computer):
            i = 1
            j = 2

    app = MyApp()
    app.cli(['--sub:file', paramfile_j3.strpath])
    assert app.sub.params() == dict(i=1, j=3)


def test_file_modifier_for_level2_par(paramfile_j3):
    class MyApp(Computer):
        class sub(Computer):
            class sub(Computer):
                i = 1
                j = 2

    app = MyApp()
    app.cli(['--sub.sub:file', paramfile_j3.strpath])
    assert app.sub.sub.params() == dict(i=1, j=3)


def test_file_modifier_for_level1_dict(paramfile_j3):
    class MyApp(Computer):
        d = Dict(default=dict(i=1, j=2))

    app = MyApp()
    app.cli(['--d:file', paramfile_j3.strpath])
    assert app.params() == dict(d=dict(i=1, j=3))


def test_file_modifier_for_level2_dict(paramfile_j3):
    class MyApp(Computer):
        class sub(Computer):
            d = Dict(default=dict(i=1, j=2))

    app = MyApp()
    app.cli(['--sub.d:file', paramfile_j3.strpath])
    assert app.sub.params() == dict(d=dict(i=1, j=3))


def test_params_option_one_file(paramfile_j3):
    class MyApp(Computer):
        j = 1

    app = MyApp()
    app.cli(['--params', paramfile_j3.strpath])
    assert app.params() == dict(j=3)


def test_params_option_two_files(tmpdir):
    class MyApp(Computer):
        class sub(Computer):
            i = 1
            j = 2

    p1 = tmpdir.join('p1.json')
    p1.write('{"sub": {"j": 3}}')
    p2 = tmpdir.join('p2.json')
    p2.write('{"sub": {"j": 4}}')

    app = MyApp()
    app.cli(['--params', p1.strpath, p2.strpath])
    assert app.sub.params() == dict(i=1, j=4)
