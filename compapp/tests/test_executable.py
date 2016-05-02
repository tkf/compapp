try:
    from unittest import mock
except ImportError:
    import mock

from ..core import Executable, Plugin


class MixinMockHooks(object):

    def __init__(self, *args, **kwds):
        super(MixinMockHooks, self).__init__(*args, **kwds)

        self.rootmock = mock.Mock()
        for hook in self.hooks:
            methodmock = mock.Mock()
            setattr(self.rootmock, hook, methodmock)
            setattr(self, hook, methodmock)


class MockExecutable(MixinMockHooks, Executable):
    hooks = ['is_loadable', 'prepare', 'run', 'save', 'load', 'finish']

    def __init__(self, *args, **kwds):
        super(MockExecutable, self).__init__(*args, **kwds)
        self.is_loadable.return_value = False


class MockPlugin(MixinMockHooks, Plugin):
    hooks = ['prepare', 'pre_run', 'post_run', 'save', 'load', 'finish']


class MockExecutableWithPlugin(MockExecutable):
    mockplugin = MockPlugin

    def __init__(self, *args, **kwds):
        super(MockExecutableWithPlugin, self).__init__(*args, **kwds)
        self.rootmock.mockplugin = self.mockplugin.rootmock


def test_executable_hooks_simple_run():
    excbl = MockExecutable()
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.is_loadable(),
        mock.call.run(),
        mock.call.save(),
        mock.call.finish(),
    ]


def test_executable_hooks_loadable_run():
    excbl = MockExecutable()
    excbl.is_loadable.return_value = True
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.is_loadable(),
        mock.call.load(),
        mock.call.finish(),
    ]


def test_plugin_hooks_simple_run():
    excbl = MockExecutableWithPlugin()
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.is_loadable(),
        mock.call.mockplugin.pre_run(),
        mock.call.run(),
        mock.call.mockplugin.post_run(),
        mock.call.save(),
        mock.call.mockplugin.save(),
        mock.call.mockplugin.finish(),
        mock.call.finish(),
    ]


def test_plugin_hooks_loadable_run():
    excbl = MockExecutableWithPlugin()
    excbl.is_loadable.return_value = True
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.is_loadable(),
        mock.call.load(),
        mock.call.mockplugin.load(),
        mock.call.mockplugin.finish(),
        mock.call.finish(),
    ]
