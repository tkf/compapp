#!/usr/bin/env python

import os
from glob import glob

basepath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "examples")

template = """\
.. _ex-{name}:

Example: `compapp.samples.{name}`
----------------------------------------------------------------------

.. literalinclude:: {path}

.. plot::

   from compapp.samples.{name} import MyApp
   MyApp({{'figure': {{'autoclose': False}}}}).execute()

"""


def generate_rst_file(rstpath, pypath):
    name = os.path.splitext(os.path.basename(pypath))[0]
    path = os.path.relpath(pypath, os.path.dirname(rstpath))
    with open(rstpath, 'w') as file:
        file.write(template.format(**locals()))


def makerst(path, rst_dir):
    if not path:
        path = glob(os.path.join(basepath, "code", "*.py"))
        path = [p for p in path if not p.endswith('__init__.py')]

    for pypath in path:
        name = os.path.splitext(os.path.basename(pypath))[0]
        rstpath = os.path.join(rst_dir, name) + '.rst'
        generate_rst_file(rstpath, pypath)


def main(args=None):
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--rst-dir", default=basepath,
                        help="generate rst files here")
    parser.add_argument("path", nargs='*')
    ns = parser.parse_args(args)
    makerst(**vars(ns))


if __name__ == '__main__':
    main()
