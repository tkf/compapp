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
     called *application* or *app*.  `compapp.apps` defines a few base
     classes for this purpose:

     .. currentmodule:: compapp.apps

     .. autosummary::

        Application
        SimulationApp
        AnalysisApp


Taxonomy of executables
=======================

Various `.Executable` subclasses provided by compapp can be understood
well when kind of computations and the type of |datastore| are
compared.

Executables with `.SubDataStore` require parent executable.  It fits
well with `DataLoader` since just loading data is useless.  It also
fits well with `Plotter` since it is a data sink, i.e., it needs data
for plotting.


.. list-table::
   :header-rows: 1

   * - Executable
     - |datastore|
     - Computation
   * - `Simulator`
     - `.DirectoryDataStore`
     - :term:`data source`
   * - `DataLoader`
     - `.SubDataStore`
     - :term:`data source`
   * - `Analyzer`
     - `.HashDataStore`
     - :term:`data sink`
   * - `Plotter`
     - `.SubDataStore`
     - :term:`data sink`
   * - `SimulationApp`
     - `.DirectoryDataStore`
     - :term:`app`
   * - `AnalysisApp`
     - `.HashDataStore`
     - :term:`app`

.. |datastore| replace:: `datastore <compapp.apps.Application.datastore>`
