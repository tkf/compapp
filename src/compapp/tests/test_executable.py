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
