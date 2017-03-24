import sys

from ..interface import Plugin
from ..descriptors import Link
from .misc import real_owner


class RecordProgramInfo(Plugin):
    meta = Link('..meta')

    def save(self):
        cls = type(real_owner(self))
        self.meta.record('programinfo', {
            'class': cls.__name__,
            'module': cls.__module__,
            'file': sys.modules[cls.__module__].__file__,
        })
