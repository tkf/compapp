=============
 Executables
=============


Kinds of computation
====================

.. currentmodule:: compapp.executables

.. glossary::

   data source

     Executable classes *not* requiring any other resources other than
     the parameters are called the *data source*.  Data source classes
     provided in `compapp.executables` are:

     .. autosummary::

        Simulator
        DataLoader

   data sink

     Executable classes requiring other resource are called the *data
     sink*.  Data sink classes provided in `compapp.executables` are:

     .. autosummary::

        Analyzer
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
well with `DataLoader` since just loading data is useless.  It also
fits well with `Plotter` since it is a data sink, i.e., it needs data
for plotting.

Since `.Analyzer` and `.Plotter` need external :term:`data source`, it
makes sense they are not subclass of `.Simulator` or `.Application`.
Typically, `.Analyzer` is used from `.AnalysisApp` combined with
`.DataLoader` or `.Simulator`.

Note that `.Simulator` exists because of implementation purpose (both
`.DataLoader` and `.Application` subclasses it; see also
:ref:`inheritance-diagram`).  It is included here for "symmetry" of
the table.  It is not recommended to use it directly and
`.SimulationApp` should always be used even when it's too simple to be
called an :term:`app`.


.. list-table::
   :header-rows: 1

   * - Executable
     - |datastore|
     - Computation
   * - `.Simulator`
     - `.DirectoryDataStore`
     - :term:`data source`
   * - `.DataLoader`
     - `.SubDataStore`
     - :term:`data source`
   * - `.Analyzer`
     - `.HashDataStore`
     - :term:`data sink`
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

.. todo:: Maybe `.Analyzer.datastore` should be `.DirectoryDataStore`.
