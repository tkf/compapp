import pkgutil

from .. import samples


def check_smoke(cls):
    app = cls()
    app.execute()


def test_smoke():
    for (_, name, ispkg) in pkgutil.iter_modules(samples.__path__):
        if ispkg:
            continue
        mod = __import__(samples.__name__ + '.' + name, fromlist=['MyApp'])
        yield (check_smoke, mod.MyApp)
