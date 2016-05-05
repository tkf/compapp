import ast
from collections import namedtuple

Option = namedtuple('Option', ['lhs', 'rhs', 'modifier'])


def parse_key(key):
    try:
        mod = ast.parse(key)
    except SyntaxError as err:
        n = err.offset-1
        if key[n] == ':':
            return (ast.parse(key[:n]), ':', key[n+1:])
        lhs, rest = key[:n].rsplit('=', 1)
        return (ast.parse(lhs), '=', rest + key[n:])
    (node,) = mod.body
    if isinstance(node, ast.Assign):
        assert len(node.targets) == 1
        return (node.targets[0], '=', key[node.value.col_offset:])
    return (node, None, None)


def parse_assignment_options(arguments):
    """
    Parse assignment options (e.g., --dict['key']).
    """
    options = []
    positional = []
    argiter = iter(arguments)
    while True:
        try:
            arg = next(argiter)
        except StopIteration:
            return (options, positional)
        if arg == '--':
            positional.extend(argiter)
            continue
        if arg.startswith('--') and arg[2:3].isalpha():
            lhs, sym, rest = parse_key(arg[2:])
            if sym == ':':
                if '=' in rest:
                    mod, v = rest.split('=', 1)
                    v0 = (v,)
                else:
                    mod = rest
                    v0 = ()
                if mod.isdigit():
                    shift = mod = int(mod)
                    if v0:
                        shift -= 1
                    if shift == 0:
                        v1 = ()
                    else:
                        _, v1 = zip(*zip(range(shift), argiter))
                    options.append(Option(lhs, v0 + v1, mod))
                elif v0:
                    options.append(Option(lhs, v0[0], mod))
                else:
                    options.append(Option(lhs, next(argiter), rest))
            elif sym == '=':
                options.append(Option(lhs, rest, None))
            else:
                options.append(Option(lhs, next(argiter), None))
        else:
            positional.append(arg)
