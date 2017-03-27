import itertools

from .base import dotted_to_nested, deepmixdicts
from .core import Parametric
from .apps import Computer
from .descriptors import Dict, OfType, Choice, dynamic_class


class ParamBuilder(Parametric):

    choices = Dict(str, (list, tuple), default={})
    ranges = Dict(str, (list, tuple), default={})
    linspaces = Dict(str, (list, tuple), default={})
    logspaces = Dict(str, (list, tuple), default={})

    def build_params(self):
        import numpy
        names = list(self.choices)
        values = [self.choices[k] for k in names]
        for key, args in self.ranges.items():
            names.append(key)
            values.append(numpy.arange(*args))
        for key, args in self.linspaces.items():
            names.append(key)
            values.append(numpy.linspace(*args))
        for key, args in self.logspaces.items():
            names.append(key)
            values.append(numpy.logspace(*args))
        return (dotted_to_nested(dict(zip(names, xs)))
                for xs in itertools.product(*values))

    def keys(self):
        return itertools.chain(
            self.choices,
            self.ranges,
            self.linspaces,
            self.logspaces,
        )


def execute(arg):
    cls, param = arg
    app = cls(param)
    app.execute()
    return app


class Variator(Computer):

    base, classpath = dynamic_class(Parametric)
    builder = ParamBuilder
    processes = -1
    executor = Choice('thread', 'process', 'dumb')
    datastore_format = '{}'
    variants = OfType(list, isparam=False)

    def run(self):
        processes = None if self.processes == -1 else self.processes

        if self.executor == 'dumb':
            pmap = map
        else:
            if self.executor == 'thread':
                # Note: multiprocessing.dummy implements threading pool
                from multiprocessing.dummy import Pool
            else:
                from multiprocessing import Pool
            pool = Pool(processes)
            pmap = pool.map

            self.defer()(pool.close)
            # Got "RuntimeError: can't start new thread" if I don't
            # close the pool.

        base = self.base.params(nested=True)

        if self.datastore.is_writable():
            def auxparam(i):
                return dict(datastore=dict(dir=self.datastore.path(
                    self.datastore_format.format(i))))
        else:
            def auxparam(i):
                return {}

        self.variants = list(pmap(
            execute,
            ((self.__class__.classpath.getclass(self),
              deepmixdicts(base, auxparam(i), param))
             for i, param in enumerate(self.builder.build_params()))))
