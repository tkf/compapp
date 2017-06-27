import json
import stat

import pytest

from ..executables import Assembler

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


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
        self.log.error('Hello from run method.')

    def load(self):
        self.runpath = 'load'
        self.log.error('Hello from load method.')


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


def test_rerun_should_overwrite(tmpdir):
    """
    Re-running executable should overwrite existing datastore.
    """
    tmpdir.join('params.json').write('broken JSON')
    params_path = str(tmpdir.join('params.json'))

    with open(params_path) as file:
        with pytest.raises(JSONDecodeError):
            json.load(file)

    app = RecordRunPath()
    app.datastore.dir = str(tmpdir)
    app.execute()

    with open(params_path) as file:
        json.load(file)


def test_force_load_should_not_overwrite_meta_data(tmpdir):
    """
    Executable loaded from datastore should not overwrite existing meta data.
    """
    app1 = RecordRunPath()
    app1.datastore.dir = str(tmpdir)
    app1.execute()

    app2 = RecordRunPath()
    app2.datastore.dir = str(tmpdir)
    app2.mode = 'load'
    app2.execute()

    app2.magics.meta.record('spam', {})
    with open(str(tmpdir.join('meta.json'))) as file:
        metadata = json.load(file)
    assert 'spam' not in metadata

    assert not app2.datastore.is_writable()


def test_force_load_should_not_overwrite_log_file(tmpdir, capsys):
    """
    Executable loaded from datastore should not overwrite existing log file.
    """
    app1 = RecordRunPath()
    app1.log.level = 'info'
    app1.datastore.dir = str(tmpdir)
    app1.execute()
    _, stderr1 = capsys.readouterr()

    app2 = RecordRunPath()
    app2.datastore.dir = str(tmpdir)
    app2.mode = 'load'
    app2.execute()
    _, stderr2 = capsys.readouterr()

    logtext = tmpdir.join('run.log').read()
    assert 'Hello from run method.' in logtext
    assert 'Hello from load method.' not in logtext
    assert 'Hello from run method.' in stderr1
    assert 'Hello from load method.' in stderr2
    assert app2.log.level == app1.log.level
    # FIXME: There is a bug so that the above line of stderr2 fails.
    # Namely, the dumped parameters are not available at the time
    # logger is configured.  Let's not fix the bug at the moment since
    # removing logger plugin is better approach.

    # Side note: Although ``app2.log.level == app1.log.level``, the
    # loggers' level are different due to the aforementioned bug.
    # Uncomment the following line to see it:
    # assert app2.log.logger.getEffectiveLevel() \
    #     == app1.log.logger.getEffectiveLevel()

    assert not app2.datastore.is_writable()


def test_force_load_non_existing_datastore(tmpdir):
    """
    Trying to load from non-existing datastore should fail.
    """
    app = RecordRunPath()
    app.datastore.dir = str(tmpdir.join('nonexisting'))
    app.mode = 'load'
    with pytest.raises(RuntimeError):
        app.execute()


def test_force_load_invalid_datastore(tmpdir):
    """
    Trying to load from invalid datastore should fail.
    """
    app = RecordRunPath()
    app.datastore.dir = str(tmpdir)
    app.mode = 'load'
    with pytest.raises(IOError):
        app.execute()
