# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
# [[[end]]]

__version__ = '0.0.0'
__author__ = 'Takafumi Arakaki'
__license__ = None

# FIXME: no stars!
from .core import *
from .executables import *
from .descriptors import *
from .plugins import *
from .apps import *
from .variator import Variator
