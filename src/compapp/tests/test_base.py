import pickle

from ..base import Unspecified


def test_unspecified_pickleable():
    assert pickle.loads(pickle.dumps(Unspecified)) is Unspecified


def test_unspecified_repr():
    assert repr(Unspecified) == 'Unspecified'


def test_unspecified_bool():
    assert not Unspecified
