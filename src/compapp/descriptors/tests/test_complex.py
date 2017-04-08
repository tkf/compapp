from ...core import Parametric
from .. import Or, Link, OfType


class Pluggy(Parametric):
    fallback = Or(OfType(bool), Link('...pluggy.fallback'), default=False)


class Nestable(Parametric):
    pluggy = Pluggy


class Root(Nestable):
    class sub(Nestable):
        class sub(Nestable):
            class sub(Nestable):
                class sub(Nestable):
                    pass


def assert_fallbacks_are(app, what):
    assert (app.pluggy.fallback
            is app.sub.pluggy.fallback
            is app.sub.pluggy.fallback
            is app.sub.sub.pluggy.fallback
            is app.sub.sub.pluggy.fallback
            is app.sub.sub.sub.pluggy.fallback
            is app.sub.sub.sub.sub.pluggy.fallback
            is what)

def dassert_fallbacks_are(obj, what):
    while True:
        assert obj.pluggy.fallback is what
        try:
            obj = obj.sub
        except AttributeError:
            return


def test_propagation():
    app = Root()
    assert_fallbacks_are(app, False)
    app.pluggy.fallback = True
    assert_fallbacks_are(app, True)
    app.sub.pluggy.fallback = False
    assert app.pluggy.fallback is True
    dassert_fallbacks_are(app.sub, False)
