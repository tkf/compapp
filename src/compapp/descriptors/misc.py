from ..core import Descriptor


class Constant(Descriptor):

    """
    Convenient descriptor for declaring non-parametric property.

    >>> from compapp import Parametric, Constant
    >>> class MyApp(Parametric):
    ...     c = Constant(1)
    >>> app = MyApp()
    >>> app.c
    1
    >>> app.c = 2
    Traceback (most recent call last):
      ...
    TypeError: can't set attributes <....MyApp ...>.c
    >>> app.c
    1

    """

    def __init__(self, value):
        super(Constant, self).__init__(value)

    def get(self, _):
        return self.default

    def __set__(self, obj, value):
        myname = self.myname(obj)
        raise TypeError("can't set attributes {0!r}.{1}".format(obj, myname))
