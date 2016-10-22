import os
import subprocess
import sys

from ..core import Plugin
from ..descriptors import Link
from .misc import real_owner


class Git(object):

    vcstype = 'git'
    git_cmd = ('git',)

    def __init__(self, filepath):
        self.filepath = filepath
        self.dirpath = os.path.dirname(filepath)
        self.root = self._get_root()

    def git(self, *cmd):
        return subprocess.check_output(self.git_cmd + cmd,
                                       universal_newlines=True,
                                       cwd=self.dirpath)

    def _get_root(self):
        try:
            return self.git('rev-parse', '--show-toplevel').strip()
        except (subprocess.CalledProcessError, OSError):
            return None

    def revision(self):
        return self.git('rev-parse', 'HEAD').strip()

    def isclean(self):
        return not bool(self.git('status', '--short').strip())

    def vcsinfo(self):
        return dict(
            vcs=self.vcstype,
            root=self.root,
            revision=self.revision(),
            isclean=self.isclean(),
            filepath=self.filepath,
        )


def getvcs(filepath):
    vcs_candidates = [cls(filepath) for cls in [Git]]
    depth, vcs = max(((-1 if vcs.root is None else len(vcs.root)), vcs)
                     for vcs in vcs_candidates)
    if depth < 0:
        return
    return vcs


class RecordVCS(Plugin):

    """
    Record VCS revision automatically.

    Example
    -------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> from compapp.apps import Computer
    >>> app = Computer()
    >>> app.datastore.dir = 'out'
    >>> app.execute()
    >>> vcsinfo = app.magics.meta.data['vcs']
    >>> sorted(vcsinfo)
    ['filepath', 'isclean', 'revision', 'root', 'vcs']
    >>> from compapp import apps
    >>> apps.__file__ == vcsinfo['filepath']
    True
    >>> vcsinfo['vcs']
    'git'

    VCS information is loaded when the app is executed in load mode:

    >>> app2 = Computer()
    >>> app2.mode = 'load'
    >>> app2.datastore.dir = 'out'
    >>> app2.execute()
    >>> app2.magics.meta.data['vcs'] == vcsinfo
    True

    """

    meta = Link('..meta')

    def pre_run(self):
        cls = type(real_owner(self))
        filepath = sys.modules[cls.__module__].__file__
        vcs = getvcs(filepath)
        if vcs:
            self.meta.record('vcs', vcs.vcsinfo())
