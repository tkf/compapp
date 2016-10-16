import datetime
try:
    import resource
except ImportError:
    resource = None

from ..core import Plugin
from ..descriptors import Link

_utc_zero = datetime.datetime.utcfromtimestamp(0)


def unixtimenow():
    """
    Return current Unix time as a float.

    Unix time (aka POSIX time or Epoch time) is defined as:

      the number of seconds that have elapsed since 00:00:00
      Coordinated Universal Time (UTC), Thursday, 1 January 1970, not
      counting leap seconds

      --- https://en.wikipedia.org/wiki/Unix_time

    """
    return (datetime.datetime.utcnow() - _utc_zero).total_seconds()


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
        unixtime=unixtimenow(),
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

    >>> timing = app.magics.metastore.data['timing']
    >>> (timing['post']['rusage']['ru_utime']
    ... + timing['post']['rusage']['ru_stime']
    ... - timing['pre']['rusage']['ru_utime']
    ... - timing['pre']['rusage']['ru_stime']) < 1.5
    True
    >>> 0.5 < timing['post']['unixtime'] - timing['pre']['unixtime'] < 1.5
    True

    """

    metastore = Link('..metastore')

    def pre_run(self):
        self.timing = {}
        self.timing['pre'] = gettimings()

    def post_run(self):
        self.timing['post'] = gettimings()
        self.metastore.record('timing', self.timing)
