from socket import gethostname
import os
import sys

from .. import __version__
from ..interface import Plugin
from ..descriptors import Link, Root
from .misc import real_owner


class RecordSysInfo(Plugin):
    meta = Link('..meta')
    root = Root()

    def pre_run(self):
        owner = real_owner(self)
        if owner is not self.root:
            return

        sysdict = {}
        for key in [
                'argv',
                'path',
                'version',
                'version_info',
        ]:
            sysdict[key] = getattr(sys, key)
        sysdict['version_info'] = tuple(sysdict['version_info'])  # for Py 2.7

        self.meta.record('sysinfo', dict(
            hostname=gethostname(),
            cwd=os.getcwd(),
            environ=dict(os.environ),
            sys=sysdict,
            compapp_version=__version__,
        ))
