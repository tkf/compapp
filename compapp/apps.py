"""
Application base classes.

.. inheritance-diagram::
   Application
   SimulationApp
   AnalysisApp
   :parts: 1

"""

from .core import Executable


class Application(Executable):

    """
    Application base class.

    Examples
    --------

    **Strict attribute.**
    `Application` subclass does not allow setting attribute other than
    its parameter or result (specified by :attr:`result_names`).
    This makes sure that `Application` holds the same data after `run`
    and `load`.

    >>> class MyApp(Application):
    ...    result_names = ('alpha', 'beta')
    >>> app = MyApp()
    >>> app.alpha = 1.0
    >>> app.gamma
    Traceback (most recent call last):
      ...
    AttributeError: 'MyApp' object has no attribute 'gamma'

    """

    result_names = ()
    """
    Names of attributes allowed to be set.  A list of `str`.
    """


class SimulationApp(Application):

    """
    """


class AnalysisApp(Application):

    """
    """
