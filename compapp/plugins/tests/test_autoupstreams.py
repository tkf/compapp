from ...executables import Assembler
from ...descriptors import Link
from ..misc import AutoUpstreams, is_runnable

ORDER = []


class AlwaysReady(Assembler):
    def run(self):
        self.done = True
        ORDER.append(self.__class__)


class DependsOnAlwaysReady(AlwaysReady):
    alwaysready_done = Link('..alwaysready.done')


class DependsOnDepAR(AlwaysReady):
    depar_done = Link('..depar.done')


class DependsOnTwo(DependsOnDepAR):
    depdepar_done = Link('..depdepar.done')


class RootApp(Assembler):
    autoupstreams = AutoUpstreams

    alwaysready = AlwaysReady
    depar = DependsOnAlwaysReady
    depdepar = DependsOnDepAR
    deptwo = DependsOnTwo


def test_execute():
    ORDER[:] = []
    app = RootApp()
    app.execute()
    assert ORDER == [
        AlwaysReady,
        DependsOnAlwaysReady,
        DependsOnDepAR,
        DependsOnTwo,
    ]


def test_is_runnable_simple():
    app = RootApp()
    assert is_runnable(app.alwaysready)
    assert not is_runnable(app.depar)
