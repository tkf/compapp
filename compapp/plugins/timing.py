import time
try:
    import resource
except ImportError:
    resource = None

from ..interface import Plugin
from ..descriptors import Link


def _getrusage_self():
    """
    See: getrusage(2)
    """
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    return {k: getattr(rusage, k) for k in dir(rusage) if k.startswith('ru_')}

if resource is None:
    def getrusage_self():
        return {}
else:
    getrusage_self = _getrusage_self


def gettimings():
    return dict(
        time=time.time(),
        rusage=getrusage_self(),
    )


class RecordTiming(Plugin):

    """
    Record timing information.

    >>> import time
    >>> from compapp.apps import Computer
    >>> class MyApp(Computer):
    ...     def run(self):
    ...         time.sleep(0.5)
    >>> app = MyApp()
    >>> app.execute()

    >>> timing = app.magics.meta.data['timing']
    >>> (timing['post']['rusage']['ru_utime']
    ... + timing['post']['rusage']['ru_stime']
    ... - timing['pre']['rusage']['ru_utime']
    ... - timing['pre']['rusage']['ru_stime']) < 1.5
    True
    >>> 0.5 < timing['post']['time'] - timing['pre']['time'] < 1.5
    True

    """

    meta = Link('..meta')

    def pre_run(self):
        self.timing = {}
        self.timing['pre'] = gettimings()

    def post_run(self):
        self.timing['post'] = gettimings()
        self.meta.record('timing', self.timing)
