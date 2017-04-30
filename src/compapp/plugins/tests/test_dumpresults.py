import pytest
import numpy
import pandas

from ... import Computer
from ...testing import assert_equal


@pytest.mark.parametrize('results', [
    [dict(a=1), dict(a=2)],
    [dict(a=numpy.arange(3)), dict(a=numpy.arange(3) + 1)],
    [dict(a=pandas.DataFrame([1])),
     dict(a=pandas.DataFrame([2]))],
])
def test_save_maybe(results, tmpdir):
    class App(Computer):
        def run(self):
            for data in results:
                for k, v in data.items():
                    self.results[k] = v

                self.magics.dumpresults.save_maybe()
                self.magics.dumpresults._bg_result.get()  # wait save

                midway = App()
                midway.datastore.dir = self.datastore.dir
                midway.magics.dumpresults.load()

                assert_equal(midway.results, self.results)

    app = App()
    app.datastore.dir = str(tmpdir)
    app.execute()

    mixed = {}
    for data in results:
        mixed.update(data)

    loader = App()
    loader.datastore.dir = app.datastore.dir
    loader.mode = 'load'
    loader.execute()
    assert_equal(loader.results, app.results)
