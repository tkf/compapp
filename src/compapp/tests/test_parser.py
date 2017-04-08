import ast
import mock

import pytest

from ..parser import Option, parse_assignment_options, assign_option


def assert_ast_eq(actual, desired):
    def normalize(n):
        if isinstance(n, ast.Module):
            assert len(n.body) == 1
            n = n.body[0]
        if isinstance(n, ast.Expression):
            n = n.body
        if isinstance(n, ast.Expr):
            n = n.value
        return n
    actual_n = normalize(actual)
    desired_n = normalize(desired)
    if hasattr(desired_n, 'ctx'):
        actual_n.ctx = desired_n.ctx
    assert ast.dump(actual_n) == ast.dump(desired_n)


def assert_opt_eq(actual, desired):
    assert_ast_eq(actual[0], desired[0])
    assert actual[1:] == desired[1:]


@pytest.mark.parametrize(
    "arguments, lhs, rhs, modifier", [
        (['--a=x'], 'a', 'x', None),
        (['--a', 'x'], 'a', 'x', None),
        (['--a:1=x'], 'a', ('x',), 1),
        (['--a:1', 'x'], 'a', ('x',), 1),
        (['--a:3=x', 'y', 'z'], 'a', ('x', 'y', 'z'), 3),
        (['--a:3', 'x', 'y', 'z'], 'a', ('x', 'y', 'z'), 3),
        (['--a:b=x'], 'a', 'x', 'b'),
        (['--a:b', 'x'], 'a', 'x', 'b'),
        (['--a["k"]=x'], 'a["k"]', 'x', None),
        (['--a["k"]:1=x'], 'a["k"]', ('x',), 1),
    ])
def test_one_opt(arguments, lhs, rhs, modifier):
    desired = Option(ast.parse(lhs), rhs, modifier)
    opts, args = parse_assignment_options(arguments)
    assert args == []
    assert len(opts) == 1
    assert_opt_eq(opts[0], desired)


@pytest.mark.parametrize(
    "arguments, opts, poss", [
        ([], [], []),
        (['a'], [], ['a']),
        (['a', '--', '--b', 'c'], [], ['a', '--b', 'c']),
        (['a', '--b', 'c', 'd'],
         [Option(ast.parse('b'), 'c', None)],
         ['a', 'd']),
    ])
def test_positional(arguments, opts, poss):
    opts_got, poss_got = parse_assignment_options(arguments)
    assert poss_got == poss
    assert len(opts_got) == len(opts)
    for actual, desired in zip(opts_got, opts):
        assert_opt_eq(actual, desired)


@pytest.mark.parametrize(
    "code", [
        'a',
        'a.b',
        'a.b.c',
        'a.b.c.d',
        'a[1].b',
    ])
def test_assign_option_ends_with_attr(code, rhs=1):
    obj = mock.MagicMock()
    lhs = ast.parse(code, mode='eval').body
    assign_option(obj, lhs, rhs)
    got = eval("obj." + code, dict(obj=obj))
    assert got == rhs


@pytest.mark.parametrize(
    "head, key", [
        ('a', 1),
        ('a[1].b', 2),
    ])
def test_assign_option_ends_with_item(head, key, rhs=1):
    code = head + '[' + repr(key) + ']'
    obj = mock.MagicMock()
    lhs = ast.parse(code, mode='eval').body
    assign_option(obj, lhs, rhs)
    got = eval("obj." + head, dict(obj=obj))
    got.__setitem__.assert_called_once_with(key, rhs)
