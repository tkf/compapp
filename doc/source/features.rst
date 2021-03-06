==================
 What is compapp?
==================


Automatic data directory naming, creation and management
========================================================

When writing programs for numerical simulations and data analysis,
managing directories to store resulting data (called :term:`datastore`
in this document) is hard.

.. |datastore| replace:: `datastore <compapp.executables.Assembler.datastore>`

.. list-table::
   :header-rows: 1
   :widths: 1 1 5

   * - `.Computer` & `.Executable` subclasses
     - |datastore| property
     - Behavior
   * - `.Computer`
     - `.DirectoryDataStore`
     - Simulation is run with a specified data directory in which
       simulation parameters and results are saved.  :term:`Nested
       classes <nested class>` such as `.Plotter` and other nested
       `.Computer`\ s may use sub-paths.
   * - :term:`nested <nested class>` `.Computer`
     - `.DirectoryDataStore`
     - If a `.Computer` subclass nests in some :term:`owner app`,
       `.DirectoryDataStore` automatically allocates sub-directory
       under the directory used by the :term:`owner app`.
   * - `.Plotter`, `.Loader`
     - `.SubDataStore`
     - Use files under the directory of the :term:`owner app`.
   * - `.Memoizer`
     - `.HashDataStore`
     - Data analysis is run with a data directory automatically
       allocated depending on the parameter values (including data
       files).  The rationale here is that data analysis has to yield
       the same result given parameters.  Thus, if the datastore
       already exists when this application is run, it loads the
       results rather than re-computing them.  In other words,
       combinations of `.Memoizer` act as build dependencies
       defined by Makefile and similar build tools.  Since generated
       datastore path is not human friendly (it is based on hash),
       compapp provides :ref:`command line interface <cli>` to help
       house-keeping.


Parameter management
====================

Simulations and data analysis require various parameters for each run.
Those parameters often have nested sub-parameters reflecting
sub-simulations and sub-analysis.  compapp naturally supports such
nested parameters using :term:`nested class`.  See `.Parametric`.

When parameters have deeply nested structure, it is hard to run a
simulation or analysis with slightly different parameters.
`.Computer.cli` provides a CLI to set such "deep parameters" on the
fly.


Automatic type-check and value-check for properties (traits)
============================================================

Simulations and data analysis require certain type of parameters but
checking them manually is hard and letting an error to happen at the
very end of long-running computations is not an option.  compapp
provides a very easy way to configure such type checks.  The main idea
implemented in `.Parametric` is that, for simple Python data types,
the default values define required data type:

>>> from compapp import Parametric
>>> class MyParametric(Parametric):
...     i = 1
...     x = 2.0
>>> MyParametric(i=1.0)          # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
    ...
ValueError: Value 1.0 (type: float) cannot be assigned to the variable
MyParametric.i (default: 1) which only accepts one of the following types:
int, int16, ...
>>> MyParametric(x='2.0')        # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
    ...
ValueError: Value '2.0' (type: str) cannot be assigned to the variable
MyParametric.x (default: 2.0) which only accepts one of the following types:
float, float16, ...

For more complex control, there are :term:`descriptors <descriptor>`
such as `.Instance`, `.Required`, `.Optional`, etc.  Collection-type
descriptors such as `.List` and `.Dict` restricts data types of its
component (e.g., dict key has to be a string and the value has to be
int) and other traits such as maximal length.  The descriptor
`.Choice` restricts the *value* of properties, rather than the type.
The descriptor `.Or` defines a property that must satisfy one of
defined restrictions.


Linking properties
==================

compapp prefers :term:`composition over inheritance`.  However, using
composition makes it hard to share properties between objects whereas
in inheritance it is easy (or too easy [#]_) to share properties
between parent and sub classes.  compapp provides various *linking
properties* (`.Link`, `.Delegate`, etc.) which can refer to properties
of other objects.

.. [#] In other words, sharing properties is opt-in for composition
   approach and forced for inheritance approach.


Hooks
=====

`.Executable` defines various methods :term:`to be extended` where
user's simulation and data analysis classes can hook some
computations.  User should at least extend the `run <.Executable.run>`
method to implement some computations.  Although methods `save
<.Executable.save>` and `load <.Executable.load>` can also be
extended, `.AutoDump` plugin can handle saving and loading results and
parameters automatically.  There are `.prepare` and `.finish` methods
to be called always, not depending on whether the executable class is
`run <.Executable.run>` or `load <.Executable.load>`\ ed.

See also: :ref:`api`


Plugins
=======

`.Executable` (hence `.Computer`) provides various hooks so that it
is easy to "inject" some useful functions via plugins.  In fact, the
main aim of compapp is to provide well-defined set of hooks and a
system for easily coordinating different components by `linking
properties`_.

Here is the list of plugins provided by `compapp.plugins`:


.. currentmodule:: compapp.plugins

.. autosummary::
   :nosignatures:

   recorders.DumpResults
   recorders.DumpParameters
   timing.RecordTiming
   vcs.RecordVCS
   misc.Logger
   misc.Debug
   misc.Figure
   datastores.DirectoryDataStore
   datastores.SubDataStore
   datastores.HashDataStore
