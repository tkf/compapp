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


.. list-table::
   :header-rows: 1

   * - Executable
     - |datastore|
     - Computation
     - Plugins
   * - `.Simulator`
     - `.DirectoryDataStore`
     - :term:`data source`
     - `.AutoDump`
   * - `.DataLoader`
     - `.SubDataStore`
     - :term:`data source`
     -
   * - `.Analyzer`
     - `.HashDataStore`
     - :term:`data sink`
     - `.AutoDump`
   * - `.Plotter`
     - `.SubDataStore`
     - :term:`data sink`
     -
   * - `.SimulationApp`
     - `.DirectoryDataStore`
     - :term:`app`
     - `.AutoDump`, `.RecordVCS`, `.RecordTiming`, `.DumpParameters`,
       etc.
   * - `.AnalysisApp`
     - `.HashDataStore`
     - :term:`app`
     - (ditto)

.. |datastore| replace:: `datastore <compapp.apps.Application.datastore>`

.. todo:: It makes sense for `.Analyzer` to not have an entry point
   (i.e., not an app) and so it make sense to have
   `.Analyzer`-`AnalysisApp` distinction.  However, why one needs
   `.Simulator`-`SimulationApp` distinction?  **Isn't it nice if every
   simulator has CLI and so is runnable?**

   How about distinction along the plugins axis?  `.Simulator` and
   `SimulationApp` are using different set of plugins.  But probably
   they shouldn't.  For example, `.RecordVCS` should be turned off
   automatically for sub-apps (or the result can be cached).  It means
   that having `.RecordVCS` in `.Simulator` does not hurt.  I'd like
   to combine different applications together so this auto-off feature
   should be implemented and so cannot be the reason for the
   distinction.

.. todo:: Maybe `.Analyzer.datastore` should be `.DirectoryDataStore`.
