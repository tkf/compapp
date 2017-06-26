from __future__ import print_function

from .base import MultiException, props_of
from .core import Parametric, Defer
from .descriptors import OfType
from .strict import MixinStrict


class Executable(MixinStrict, Parametric):

    """
    The base class supporting execution and plugin mechanism.

    Example
    -------
    >>> class MyPlugin(Plugin):
    ...     def pre_run(self):
    ...         print('Pre-run:', self.__class__.__name__)
    ...
    >>> class MyExec(Executable):
    ...     myplugin = MyPlugin
    ...
    ...     def run(self):
    ...         print('Run:', self.__class__.__name__)
    ...
    >>> excbl = MyExec()
    >>> excbl.execute()
    Pre-run: MyPlugin
    Run: MyExec

    """

    defer = OfType(Defer, isparam=False)

    def __init__(self, *args, **kwds):
        super(Executable, self).__init__(*args, **kwds)
        self.defer = Defer()

    def execute(self, *args):
        """
        Execute this instance.

        Basically, this function does this:

        .. parsed-literal::

           `.prepare()`
           `Plugin.prepare()`
           if `.should_load()`:
               `.load()`
               `Plugin.load()`
           else:
               `Plugin.pre_run()`
               `.run()`
               `Plugin.post_run()`
               `.save()`
               `Plugin.save()`
           `Plugin.finish()`
           `.finish()`

        Note that ``Plugin.<method>()`` are run for all plugins.

        """
        try:
            self.prepare()
            call_plugins(self, 'prepare')
            if self.should_load():
                self.load()
                call_plugins(self, 'load')
            else:
                call_plugins(self, 'pre_run')
                self.run(*args)
                call_plugins(self, 'post_run')
                self.save()
                call_plugins(self, 'save')
            call_plugins(self, 'finish')
            self.finish()
        # except Exception as err:
        #     self.onerror(err)
        #     raise
        finally:
            MultiException.run([
                (call_plugins, self, '_defer_call'),
                self.defer.call,
            ])

    def should_load(self):
        """
        Return `True` if `.load` should be run.

        Default is to return `False` always.
        See also `.Assembler.is_loadable`.

        """
        return False

    def prepare(self):
        """
        |TO BE EXTENDED| Prepare for `run`/`load`; e.g., execute upstreams.
        """

    def run(self, *args):
        """
        |TO BE EXTENDED| Do the actual simulation/analysis.
        """

    def save(self):
        """
        |TO BE EXTENDED| Save the result manually.
        """

    def load(self):
        """
        |TO BE EXTENDED| Load saved result manually.
        """

    def finish(self):
        """
        |TO BE EXTENDED| Do anything to be done before exit.
        """


def call_plugins(self, method):
    from .plugins import BaseDataStore
    from .plugins import Logger
    order = {
        BaseDataStore: 0,
        Logger: 1,
    }
    # FIXME: Remove sorting or turn this into a public API.  This is a
    # hack to ensure that datastore is available before any .prepare
    # methods, specifically in Logger.prepare.
    for plugin in sorted(props_of(self, Plugin),
                         key=lambda plugin: order.get(type(plugin), 100)):
        getattr(plugin, method)()


class Plugin(Parametric):

    """
    Plugin base class.
    """

    def __init__(self, *args, **kwds):
        super(Plugin, self).__init__(*args, **kwds)
        self.defer = Defer()

    def _defer_call(self):
        self.defer.call()

    def prepare(self):
        """
        |TO BE EXTENDED| For a task immediately *after* `Executable.prepare`.
        """

    def pre_run(self):
        """
        |TO BE EXTENDED| For a task immediately before `Executable.run`.
        """

    def post_run(self):
        """
        |TO BE EXTENDED| For a task immediately after `Executable.run`.
        """

    def save(self):
        """
        |TO BE EXTENDED| For a task immediately *after* `Executable.save`.
        """

    def load(self):
        """
        |TO BE EXTENDED| For a task immediately *before* `Executable.load`.
        """

    def finish(self):
        """
        |TO BE EXTENDED| For a task immediately *before* `Executable.finish`.
        """
