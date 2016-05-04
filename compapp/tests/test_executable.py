try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from ..base import MultiException
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
    hooks = ['should_load', 'prepare', 'run', 'save', 'load', 'finish']

    def __init__(self, *args, **kwds):
        super(MockExecutable, self).__init__(*args, **kwds)
        self.should_load.return_value = False


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
        mock.call.should_load(),
        mock.call.run(),
        mock.call.save(),
        mock.call.finish(),
    ]


def test_executable_hooks_loadable_run():
    excbl = MockExecutable()
    excbl.should_load.return_value = True
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.should_load(),
        mock.call.load(),
        mock.call.finish(),
    ]


def test_plugin_hooks_simple_run():
    excbl = MockExecutableWithPlugin()
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.should_load(),
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
    excbl.should_load.return_value = True
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.should_load(),
        mock.call.load(),
        mock.call.mockplugin.load(),
        mock.call.mockplugin.finish(),
        mock.call.finish(),
    ]


def test_plugin_hooks_with_a_deferred_calls():
    excbl = MockExecutableWithPlugin()
    excbl.mockplugin.defer()(excbl.rootmock.mockplugin.defer.call)
    excbl.execute()
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.should_load(),
        mock.call.mockplugin.pre_run(),
        mock.call.run(),
        mock.call.mockplugin.post_run(),
        mock.call.save(),
        mock.call.mockplugin.save(),
        mock.call.mockplugin.finish(),
        mock.call.finish(),
        mock.call.mockplugin.defer.call(),
    ]


def test_plugin_hooks_deferred_calls_on_error():
    excbl = MockExecutableWithPlugin()
    excbl.mockplugin.defer()(excbl.rootmock.mockplugin.defer.call)
    excbl.run.side_effect = raised = RuntimeError("dummy error")
    with pytest.raises(RuntimeError) as excinfo:
        excbl.execute()
    assert excinfo.value is raised
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.should_load(),
        mock.call.mockplugin.pre_run(),
        mock.call.run(),
        mock.call.mockplugin.defer.call(),
    ]


def test_plugin_hooks_one_error_in_deferred_call():
    excbl = MockExecutableWithPlugin()
    raised = RuntimeError("dummy error")
    excbl.rootmock.mockplugin.defer.call.side_effect = raised
    excbl.mockplugin.defer()(excbl.rootmock.mockplugin.defer.call)
    with pytest.raises(MultiException) as excinfo:
        excbl.execute()
    assert excinfo.value.errors[0].errors[0] is raised
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.should_load(),
        mock.call.mockplugin.pre_run(),
        mock.call.run(),
        mock.call.mockplugin.post_run(),
        mock.call.save(),
        mock.call.mockplugin.save(),
        mock.call.mockplugin.finish(),
        mock.call.finish(),
        mock.call.mockplugin.defer.call(),
    ]


def test_plugin_hooks_two_errors_in_deferred_call():
    excbl = MockExecutableWithPlugin()
    raised1 = RuntimeError("dummy error 1")
    raised2 = RuntimeError("dummy error 2")
    excbl.rootmock.mockplugin.defer.call1.side_effect = raised1
    excbl.rootmock.mockplugin.defer.call2.side_effect = raised2
    excbl.mockplugin.defer()(excbl.rootmock.mockplugin.defer.call1)
    excbl.mockplugin.defer()(excbl.rootmock.mockplugin.defer.call2)
    with pytest.raises(MultiException) as excinfo:
        excbl.execute()
    assert excinfo.value.errors[0].errors == [raised1, raised2]
    assert excbl.rootmock.method_calls == [
        mock.call.prepare(),
        mock.call.mockplugin.prepare(),
        mock.call.should_load(),
        mock.call.mockplugin.pre_run(),
        mock.call.run(),
        mock.call.mockplugin.post_run(),
        mock.call.save(),
        mock.call.mockplugin.save(),
        mock.call.mockplugin.finish(),
        mock.call.finish(),
        mock.call.mockplugin.defer.call1(),
        mock.call.mockplugin.defer.call2(),
    ]
