from .core import Parameter


class Link(Parameter):

    """
    """

    def __init__(self, path):
        self.path = path


class Root(Link):

    def __init__(self):
        super(Root, self).__init__('')


class Delegate(Parameter):

    """
    """


class Owner(Parameter):

    """
    """


class OwnerInfo(Parameter):

    """
    """


class Propagate(Parameter):

    """
    """


class Required(Parameter):

    """
    """

    def __init__(self, type=None):
        pass


class List(Parameter):

    """
    """


class Dict(Parameter):

    """
    """
