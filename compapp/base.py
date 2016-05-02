def constant(cls):
    """
    Pickleable singleton generator.
    """
    cls.__repr__ = cls.__reduce__ = lambda self: self.__class__.__name__
    return cls()


@constant
class Unspecified(object):
    """
    A placeholder singleton to indicate that the argument is not specified.
    """
