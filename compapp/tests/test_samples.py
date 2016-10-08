import pkgutil

import pytest

from .. import samples


@pytest.mark.parametrize(
    "cls", [
        __import__(samples.__name__ + '.' + name, fromlist=['MyApp']).MyApp
        for (_, name, ispkg) in pkgutil.iter_modules(samples.__path__)
        if not ispkg
    ])
def test_smoke(cls):
    app = cls()
    app.execute()
