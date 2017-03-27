from __future__ import print_function

import os

from .apps import Computer
from .utils.importer import import_object


def _guess_module(path):
    if not os.path.exists(path):
        raise RuntimeError('{} is not an importable path nor a file path'
                           .format(path))

    rootpath = path
    while rootpath != os.path.dirname(rootpath):
        rootpath = os.path.dirname(rootpath)
        if os.path.exists(os.path.join(rootpath, 'setup.py')):
            break
    else:
        raise RuntimeError('Cannot determine a project root path of {}'
                           .format(path))

    relpath, _ = os.path.splitext(os.path.relpath(path, rootpath))
    components = relpath.split(os.path.sep)
    return '.'.join(components)


def import_appclass(path, supcls=Computer):
    try:
        cls = import_object(path)
    except ImportError:
        return import_appclass(_guess_module(path), supcls=supcls)

    if isinstance(cls, type) and issubclass(cls, supcls):
        return cls

    try:
        modname = cls.__name__
    except AttributeError:
        return import_appclass(_guess_module(path), supcls=supcls)

    candidates = []
    for _, can in vars(cls).items():
        if not (isinstance(can, type) and issubclass(can, supcls)):
            continue
        try:
            canmod = can.__module__
        except AttributeError:
            continue
        if canmod == modname:
            candidates.append(can)
    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) == 0:
        raise RuntimeError('No subclass of {} is found in {}'
                           .format(supcls, path))
    else:
        raise RuntimeError('Too many (={}) subclasses of {} is found in {}'
                           .format(len(candidates), supcls, path))


def cli_run(path, args):
    """
    Run application class at `path` with `args`.

    Examples
    --------
    ::

      run compapp.samples.pluggable_plotter_exec.MyApp

    When there is only one `compapp.Computer` subclass in a module,
    class name can be omitted.  Thus, these are equivalent::

      run compapp.samples.simple_plots.MyApp
      run compapp.samples.simple_plots

    When ``A/B/C/D.py`` is passed as `path` and ``A/B/`` (say) is a
    project root, i.e., there is a ``A/B/setup.py`` file, then it is
    equivalent to passing the module path ``C.D``.  Thus, the
    following is equivalent to above two::

      run compapp/samples/simple_plots.py

    """
    cls = import_appclass(path)
    app = cls()
    app.cli(args)


def cli_mrun(path, args):
    """
    Run any class at `path` with different parameters.

    See help of `run` command for how `path` is interpreted.  Note
    that `path` can point to any class (not just `Computer` subclass).

    """
    from .variator import Variator
    cls = import_appclass(path, object)
    classpath = cls.__module__ + '.' + cls.__name__
    app = Variator(classpath=classpath)
    app.cli(args)


def make_parser(doc=__doc__):
    import argparse

    class FormatterClass(argparse.RawDescriptionHelpFormatter,
                         argparse.ArgumentDefaultsHelpFormatter):
        pass

    parser = argparse.ArgumentParser(
        formatter_class=FormatterClass,
        description=doc)
    parser.add_argument(
        '--pdb', dest='debugger', action='store_const', const='pdb',
    )

    # Required for Python 3:
    parser.set_defaults(func=lambda **_: parser.error('too few arguments'))

    subparsers = parser.add_subparsers()

    def subp(command, func):
        doc = func.__doc__
        title = None
        for title in filter(None, map(str.strip, (doc or '').splitlines())):
            break
        p = subparsers.add_parser(
            command,
            formatter_class=FormatterClass,
            help=title,
            description=doc)
        p.set_defaults(func=func)
        return p

    def run_arguments(p):
        p.add_argument(
            'path',
            help="""
            dotted class path (e.g.,
            compapp.samples.pluggable_plotter_exec.MyApp).
            """
        )
        p.add_argument(
            'args', nargs='*',
            help="arguments and options to the app at `path`"
        )

    p = subp('run', cli_run)
    run_arguments(p)

    p = subp('mrun', cli_mrun)
    run_arguments(p)

    return parser


def main(args=None):
    parser = make_parser()
    ns = parser.parse_args(args)
    debugger = ns.debugger
    del ns.debugger
    try:
        return (lambda func, **kwds: func(**kwds))(**vars(ns))
    except Exception:
        if debugger == 'pdb':
            import pdb
            pdb.post_mortem()
        else:
            raise


if __name__ == '__main__':
    main()
