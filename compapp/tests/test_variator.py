import pytest

from ..apps import Computer
from ..variator import Variator

# executor_choices = Variator.executor.choices
executor_choices = ['thread', 'dumb', pytest.mark.skip('process')]


class SumAB(Computer):

    a = 1.0
    b = 2.0

    def run(self):
        self.results.c = self.a + self.b


@pytest.mark.parametrize('executor', executor_choices)
def test_sumab(executor):
    app = Variator(
        classpath=__name__ + '.SumAB',
        builder=dict(ranges=dict(a=(10,))),
        executor=executor,
    )
    app.execute()
    assert [v.results.c for v in app.variants] == list(range(2, 12))


@pytest.mark.parametrize('executor', executor_choices)
def test_sumab_with_datastore(executor, tmpdir):
    app = Variator(
        classpath=__name__ + '.SumAB',
        builder=dict(ranges=dict(a=(10,))),
        executor=executor,
        datastore=dict(dir=str(tmpdir))
    )
    app.execute()

    exists = [tmpdir.join(str(i)).check() for i in range(10)]
    assert all(exists)
