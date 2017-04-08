import pytest

from ..apps import Computer


def test_strict_computer():
    app = Computer()
    with pytest.raises(AttributeError):
        app.spam = 'egg'
