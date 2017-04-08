from __future__ import print_function

import logging
import re

from ... import Computer
from .. import Logger


def test_handlers_are_copied():
    l1 = Logger()
    l2 = Logger()
    l1.handlers['console']['stream'] = 'ext://sys.stdout'
    assert l2.handlers['console']['stream'] == 'ext://sys.stderr'


def test_formatters_are_copied():
    l1 = Logger()
    l2 = Logger()
    l1.formatters['basic']['format'] = ''
    assert l2.formatters['basic']['format'] == logging.BASIC_FORMAT


LEVELS = ['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG']


class Greeter(Computer):
    message = 'hello'

    def run(self):
        self.results.isrun = True

        for lvl in LEVELS:
            getattr(self.log, lvl.lower())(self.message)

        try:
            sub = self.sub
        except AttributeError:
            return
        sub.execute()


class MyApp(Greeter):
    class sub(Greeter):
        class sub(Greeter):
            pass


def assert_levels(output, lvl):
    i = LEVELS.index(lvl) + 1
    for l in LEVELS[:i]:
        assert l in output
    for l in LEVELS[i:]:
        assert l not in output


def test_nested_simple_run(capsys):
    app = MyApp()
    app.execute()

    _, err = capsys.readouterr()
    assert app.log.level == 'ERROR'
    assert_levels(err, 'ERROR')
    assert len(re.findall('^CRITICAL .* hello$', err, re.MULTILINE)) == 3


def test_nested_root_config(capsys):
    app = MyApp()
    app.log.formatters['test'] = {'format': '! %(levelname)s ! %(message)s'}
    app.log.handlers['console']['formatter'] = 'test'
    app.execute()

    _, err = capsys.readouterr()
    assert app.log.level == 'ERROR'
    assert_levels(err, 'ERROR')
    assert len(re.findall('^! CRITICAL ! hello$', err, re.MULTILINE)) == 3

    # Make sure I didn't overwrite the default config:
    assert 'test' not in MyApp().log.formatters
    assert MyApp().log.handlers['console']['formatter'] != 'test'


def test_nested_specific_handler(capsys):
    app = MyApp()
    app.sub.log.ownconfig = True
    app.sub.log.formatters = dict(
        app.sub.sub.log.formatters,
        test={'format': '! %(levelname)s ! %(message)s'},
    )
    app.sub.log.handlers = dict(console2=dict(
        app.log.handlers['console'],
        formatter='test',
    ))
    app.execute()

    _, err = capsys.readouterr()
    assert app.log.level == 'ERROR'
    assert_levels(err, 'ERROR')
    assert len(re.findall('^! CRITICAL ! hello$', err, re.MULTILINE)) == 2


def test_datastore_log(tmpdir):
    app = MyApp()
    app.datastore.dir = tmpdir.strpath
    app.execute()

    out = open(app.datastore.path('run.log')).read()
    assert app.log.level == 'ERROR'
    assert_levels(out, 'ERROR')
    assert len(re.findall(':CRITICAL:.*:hello$', out, re.MULTILINE)) == 3
