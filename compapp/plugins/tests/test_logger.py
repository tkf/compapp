import logging

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
