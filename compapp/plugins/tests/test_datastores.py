from ...interface import Executable
from ..datastores import DirectoryDataStore


class WithStore(Executable):
    datastore = DirectoryDataStore
    exists = None

    def run(self):
        if self.datastore.dir is None:
            self.exists = None
        else:
            self.exists = self.datastore.exists()


class CheckDir(WithStore):
    class sub(WithStore):
        class sub(WithStore):
            class sub(WithStore):
                pass

    def run(self):
        super(CheckDir, self).run()
        sub = self
        while True:
            try:
                sub = sub.sub
            except AttributeError:
                break
            sub.execute()


def test_nodir():
    app = CheckDir()
    app.execute()
    assert (app.exists
            is app.sub.exists
            is app.sub.sub.exists
            is app.sub.sub.sub.exists
            is None)


def test_root_exists(tmpdir):
    app = CheckDir()
    app.datastore.dir = tmpdir.strpath
    app.execute()
    assert app.exists
    assert (app.sub.exists
            is app.sub.sub.exists
            is app.sub.sub.sub.exists
            is False)


def test_sub_exists(tmpdir):
    app = CheckDir()
    app.sub.datastore.dir = tmpdir.strpath
    app.execute()
    assert app.exists is None
    assert app.sub.exists
    assert app.sub.sub.exists is app.sub.sub.sub.exists is False
