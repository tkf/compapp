import numpy
import pandas

from .base import DictObject


def _preprocess(thing):
    if isinstance(thing, DictObject):
        thing = thing()
    if isinstance(thing, dict):
        return {k: _preprocess(v) for k, v in thing.items()}
    if isinstance(thing, pandas.core.generic.PandasObject):
        # FIXME: this does not work for Panel
        return thing.to_dict()
    return thing


def assert_equal(actual, desired, **kwds):
    __tracebackhide__ = True  # Hide traceback for py.test
    numpy.testing.assert_equal(_preprocess(actual),
                               _preprocess(desired),
                               **kwds)
