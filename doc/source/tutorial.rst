==========
 Tutorial
==========

.. Run the code below in a clean temporary directory:
   >>> getfixture('cleancwd')

>>> import os
>>> import numpy
>>> from compapp import Computer

>>> class Sine(Computer):
...     steps = 100
...     freq = 50.0
...     phase = 0.0
...
...     def run(self):
...         ts = numpy.arange(self.steps) / self.freq + self.phase
...         self.results.xs = numpy.sin(2 * numpy.pi * ts)

Call `.execute` (*not* `.run`) to run the computation:

>>> app = Sine()
>>> app.execute()
>>> app.results.xs
array([...])

Any attributes assigned to `.results` are going to be saved in
`datastore.dir <.DirectoryDataStore.dir>` if it is specified:

>>> app = Sine()
>>> app.datastore.dir = 'out'
>>> app.execute()
>>> npz = numpy.load('out/results.npz')
>>> numpy.testing.assert_equal(app.results.xs, npz['xs'])

You can also pass (nested) dictionary to the class:

>>> app = Sine({'datastore': {'dir': 'another-dir'}})
>>> app.datastore.dir
'another-dir'


Plotting
========

The `.figure` attribute of `.Computer` is a simple wrapper of
`matplotlib.pyplot`.

>>> class MyApp(Computer):
...     sine = Sine
...
...     def run(self):
...         self.sine.execute()
...         _, ax = self.figure.subplots()  # calls pyplot.subplots()
...         ax.plot(self.sine.results.xs)

>>> app = MyApp()
>>> app.datastore.dir = 'out'
>>> app.execute()

The plot is automatically saved to a file in the :term:`datastore`
directory:

>>> os.path.isfile('out/figure-0.png')
True

In interactive environments, the figures are also shown via default
matplotlib backend (e.g., as inline figures in Jupyter notebook).


Composition of computations
===========================

Since `MyApp` is built on top of `Sine`, the result of `Sine` is also
saved in the datastore of `MyApp`.

>>> os.path.isfile('out/sine/results.npz')
True

The parameter passed to the root class is passed to nested class:

>>> app = MyApp({'sine': {'phase': 0.5}})
>>> app.sine.phase
0.5

Decomposing parameters and computations in reusable building blocks
makes code simple.

For example, suppose you want to try many combinations of frequencies
and phases.  You can use `numpy.linspace` for this purpose.  Naive
implementation would be like this::

  class NaiveMultiSine(Computer):
      steps = 100

      freq_start = 10.0
      freq_stop = 100.0
      freq_num = 50

      phase_start = 0.0
      phase_stop = 1.0
      phase_num = 50

      def run(self):
          freqs = numpy.linspace(
              self.freq_start, self.freq_stop, self.freq_num)
          phases = numpy.linspace(
              self.phase_start, self.phase_stop, self.phase_num)
          ...

A better way is to use `.Parametric` and make a composable part:

>>> from compapp import Parametric
>>> class LinearSpace(Parametric):
...     start = 0.0
...     stop = 1.0
...     num = 50
...
...     @property
...     def array(self):
...         return numpy.linspace(self.start, self.stop, self.num)

Then `LinearSpace` can be used as attributes:

>>> class MultiSine(Computer):
...     steps = 100
...     phases = LinearSpace
...
...     class freqs(LinearSpace):  # subclass to change default start/stop
...         start = 10.0
...         stop = 100.0
...
...     def run(self):
...         freqs = self.freqs.array
...         phases = self.phases.array
...
...         ts = numpy.arange(self.steps)
...         xs = numpy.zeros((len(freqs), len(phases), self.steps))
...         for i, f in enumerate(freqs):
...             for j, p in enumerate(phases):
...                 xs[i, j] = numpy.sin(2 * numpy.pi * (ts / f + p))
...         self.results.xs = xs
...
>>> app = MultiSine()
>>> app.freqs.num = 10
>>> app.phases.num = 20
>>> app.execute()
>>> app.results.xs.shape
(10, 20, 100)


Dynamic loading
===============

You can switch a part of computation at execution time:

>>> class Cosine(Sine):
...     def run(self):
...         ts = numpy.arange(self.steps) / self.freq + self.phase
...         self.results.xs = numpy.cos(2 * numpy.pi * ts)

.. hack
   >>> import sys
   >>> sys.modules[__name__].Sine = Sine
   >>> sys.modules[__name__].Cosine = Cosine

>>> from compapp import dynamic_class
>>> class MyApp2(Computer):
...     signal, signal_class = dynamic_class('.Sine', __name__)
...
...     def run(self):
...         self.signal.execute()
...         _, ax = self.figure.subplots()
...         ax.plot(self.signal.results.xs)
...
>>> assert isinstance(MyApp2().signal, Sine)
>>> assert isinstance(MyApp2({'signal_class': '.Cosine'}).signal, Cosine)

.. rewind the hack:
   >>> del sys.modules[__name__].Sine
   >>> del sys.modules[__name__].Cosine


Trying out multiple parameters (in parallel)
============================================

To vary parameters of a computation, you can use the CLI bundled with
compapp:

.. code:: sh

   capp mrun DOTTED.PATH.TO.A.CLASS -- \
       '--builder.ranges["PATH.TO.A.PARAM"]:leval=(START,[ STOP[, STEP]])' \
       '--builder.linspaces["PATH.TO.A.PARAM"]:leval=(START,[ STOP[, STEP]])' \
       '--builder.logspaces["PATH.TO.A.PARAM"]:leval=(START,[ STOP[, STEP]])' \
       ...

.. hack
   >>> import sys
   >>> sys.modules[__name__].MyApp = MyApp

You can also use the same functionality in Python code:

>>> from compapp import Variator
>>> class MyVariator(Variator):
...     base, classpath = dynamic_class('.MyApp', __name__)
...
...     class builder:
...         linspaces = {
...             'sine.freq': (10.0, 100.0, 50),
...             'sine.phase': (0.0, 1.0, 50),
...         }
...
>>> app = MyVariator()
>>> app.builder.linspaces['sine.freq'] = (10.0, 100.0, 3)  # num = 3
>>> app.builder.linspaces['sine.phase'] = (0.0, 1.0, 2)  # num = 2
>>> app.execute()
>>> len(app.variants)  # = 3 * 2
6
>>> assert isinstance(app.variants[0], MyApp)

.. rewind the hack
   >>> del sys.modules[__name__].MyApp
