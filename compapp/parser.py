import argparse
import ast
import os
from collections import namedtuple

from .core import simple_types

Option = namedtuple('Option', ['lhs', 'rhs', 'modifier'])


def parse_key(key):
    try:
        expr = ast.parse(key, mode='eval')
    except SyntaxError as err:
        n = err.offset-1
        assert key[n] in (':', '=')
        return (ast.parse(key[:n], mode='eval'), key[n], key[n+1:])
    node = expr.body
    if isinstance(node, ast.Assign):
        assert len(node.targets) == 1
        lhs = node.targets[0]
        lhs.ctx = expr.ctx
        return (lhs, '=', key[node.value.col_offset:])
    node.ctx = expr.body.ctx
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


def parse_bool(value):
    if not isinstance(value, str):
        return value
    val = value.lower()
    if val in ('1', 'yes', 'true'):
        return True
    elif val in ('0', 'no', 'false'):
        return False
    return value


def parse_value(holder, name, value):
    desc = None
    try:
        desc = getattr(type(holder), name)
        parse = desc.parse
    except AttributeError:
        if isinstance(desc, str):
            return value
        elif isinstance(desc, bool):
            return parse_bool(value)
        elif isinstance(desc, simple_types):
            return type(desc)(value)
    else:
        return parse(value)
    return value


def assign_option(obj, lhs, rhs):
    try:
        ctx = lhs.ctx
    except AttributeError:
        ctx = lhs.body.ctx

    node = lhs
    if isinstance(node, ast.Expression):
        node = node.body
    if isinstance(node, ast.Expr):
        node = node.value
    if isinstance(node, ast.Name):
        setattr(obj, node.id, parse_value(obj, node.id, rhs))
        return

    root = node
    prev = None
    while True:
        if isinstance(node, ast.Name):
            break
        else:
            prev, node = node, node.value
    prev.value = ast.Attribute(value=ast.Name(id='self', ctx=ctx),
                               attr=node.id)
    ast.fix_missing_locations(root.value)
    for child in ast.walk(root.value):
        child.ctx = ctx
    holder = eval(compile(ast.Expression(body=root.value),
                          '<compapp-parser>',
                          'eval'),
                  dict(self=obj))

    if isinstance(root, ast.Attribute):
        setattr(holder, root.attr, parse_value(holder, root.attr, rhs))
    elif isinstance(root, ast.Subscript):
        idx = ast.literal_eval(root.slice.value)
        holder[idx] = rhs
        # FIXME: somehow parse_value has to be called like above, but how?
    else:
        raise ValueError("Unsupported: {0}".format(lhs))


def load_any(path):
    """
    Load any data file from given path.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pickle':
        import pickle
        loader = pickle.load
    elif ext == '.json':
        import json
        loader = json.load
    elif ext in ('.yaml', '.yml'):
        import yaml
        loader = yaml.laod
    else:
        raise ValueError('file extension of "{0}" is not recognized'
                         .format(path))
    with open(path) as file:
        return loader(file)


def process_modifier(lhs, rhs, modifier):
    if isinstance(modifier, int) or modifier is None:
        pass
    elif modifier == 'leval':
        rhs = ast.literal_eval(rhs)
    elif modifier == 'file':
        rhs = load_any(rhs)
    else:
        raise ValueError("Unsupported modifier: {0}".format(modifier))
    return lhs, rhs


def process_assignment_options(obj, options):
    for opt in options:
        assign_option(obj, *process_modifier(*opt))


def make_parser(doc=None):
    kwds = dict(description=doc, allow_abbrev=False)
    try:
        parser = argparse.ArgumentParser(**kwds)  # >= Python 3.5
    except TypeError:
        del kwds['allow_abbrev']
        parser = argparse.ArgumentParser(**kwds)
    parser.add_argument('--help-full', '-H', action='store_true',
                        help="""
                        Show full help including the full list of parameters
                        """)
    '''
    parser.add_argument('--compapp-debug', action='store_true',
                        help="""
                        Enable debugging of compapp internals.  It turn on
                        the debug flag so that errors are raised immediately
                        and various internal logs are shown in stderr.
                        """)
    '''
    return parser


def parseargs(parser, args=None):
    ns, unknown = parser.parse_known_args(args)
    opts, poss = parse_assignment_options(unknown)
    return (ns, opts, poss)
