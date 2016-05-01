=============
 Executables
=============


Kinds of computation
====================

.. currentmodule:: compapp.executables

.. glossary::

   data source

     Executable classes *not* requiring any other resources other than
     the parameters are called the *data source*.  That is to say, an
     Executable class is a data source if its :code:`run` method
     overriding `.Executable.run` does *not* taking any arguments.
     Example:

     .. autosummary::

        DataLoader

   data sink

     Executable classes requiring other resource are called the *data
     sink*.  That is to say, an Executable class is a data sink if its
     :code:`run` method overriding `.Executable.run` takes *at least
     one* argument.  Example:

     .. autosummary::

        Plotter

   app
   application

     Executable classes which orchestrate other executable classes are
     called *application* or *app*.  Note that an *app* is also a
     :term:`data source` since it does not require additional data
     source.  `compapp.apps` defines a few base classes for this
     purpose:

     .. currentmodule:: compapp.apps

     .. autosummary::

        Application
        SimulationApp
        AnalysisApp


Taxonomy of executables
=======================

Various `.Executable` subclasses provided by compapp can be understood
well when kind of computations, the type of |datastore| and used
plugins are compared.

Executables with `.SubDataStore` require parent executable.  It fits
well with `.DataLoader` since just loading data is useless.  It also
fits well with `.Plotter` since it is a data sink, i.e., it needs data
for plotting.  Since `.Plotter` needs some external :term:`data
source`, it makes sense that it is not a subclass of `.Application`.


.. list-table::
   :header-rows: 1

   * - Executable
     - |datastore|
     - Computation
   * - `.DataLoader`
     - `.SubDataStore`
     - :term:`data source`
   * - `.Plotter`
     - `.SubDataStore`
     - :term:`data sink`
   * - `.SimulationApp`
     - `.DirectoryDataStore`
     - :term:`app`
   * - `.AnalysisApp`
     - `.HashDataStore`
     - :term:`app`

.. |datastore| replace:: `datastore <compapp.apps.Application.datastore>`
