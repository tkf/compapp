import pytest

import stat

from ..executables import Assembler


def chmod_readonly_only_files(path):
    for p in path.listdir():
        p.chmod(stat.S_IRUSR)


@pytest.mark.parametrize('chmod', [
    lambda _: None,
    lambda tmpdir: tmpdir.chmod(stat.S_IRUSR | stat.S_IXUSR),
    lambda tmpdir: tmpdir.chmod(stat.S_IRUSR | stat.S_IXUSR, rec=True),
    chmod_readonly_only_files,
])
def test_load_readonly(tmpdir, chmod):
    app0 = Assembler()
    app0.datastore.dir = str(tmpdir)
    app0.results.data = {'one': 1}
    app0.execute()

    chmod(tmpdir)

    app1 = Assembler()
    app1.datastore.dir = str(tmpdir)
    app1.mode = 'load'
    app1.execute()
    assert app1.results.data == app0.results.data


class RecordRunPath(Assembler):

    runpath = None

    def run(self):
        self.results.data = {'some': 'data'}
        self.runpath = 'run'

    def load(self):
        self.runpath = 'load'


def test_auto_run(tmpdir):
    app = RecordRunPath()
    app.mode = 'auto'
    app.datastore.dir = str(tmpdir)
    app.execute()

    assert set(str(p.basename) for p in tmpdir.listdir()) == \
        {'params.json', 'meta.json', 'run.log', 'results.json'}
    assert app.runpath == 'run'


def test_auto_load(tmpdir):
    app1 = RecordRunPath()
    app1.datastore.dir = str(tmpdir)
    app1.execute()

    app2 = RecordRunPath()
    app2.datastore.dir = str(tmpdir)
    app2.mode = 'load'
    app2.execute()

    assert app2.runpath == 'load'
    assert app2.results.data == app1.results.data
