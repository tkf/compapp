==================
 What is compapp?
==================


Automatic data directory naming, creation and management
========================================================

When writing programs for numerical simulations and data analysis,
managing directories to store resulting data (called :term:`datastore`
in this document) is hard.

.. |datastore| replace:: `datastore <compapp.apps.Application.datastore>`

.. list-table::
   :header-rows: 1
   :widths: 1 1 5

   * - `.Application`/`.Executable` subclasses
     - |datastore| property
     - Behavior
   * - `.SimulationApp`
     - `.DirectoryDataStore`
     - Simulation is run with a specified data directory in which
       simulation parameters and results are saved.  :term:`Nested
       classes <nested class>` such as `Simulator` and `Plotter` may
       use sub-directories.
   * - `.AnalysisApp`
     - `.HashDataStore`
     - Data analysis is run with a data directory automatically
       allocated depending on the parameter values (including data
       files).  The rationale here is that data analysis has to yield
       the same result given parameters.  Thus, if the datastore
       already exists when this application is run, it loads the
       results rather than re-computing them.  In other words,
       combinations of `.AnalysisApp` act as build dependencies
       defined by Makefile and similar build tools.  Since generated
       datastore path is not human friendly (it is based on hash),
       compapp provides :ref:`command line interface <cli>` to help
       house-keeping.
   * - `.Plotter`
     - `.Propagate`
     - Use the |datastore| property of the application using this
       plotter (called the :term:`owner app` or :term:`owner class`).
   * - `.Simulator`
     - `.SubDataStore`
     - Use sub-directory of the datastore directory used by the
       :term:`owner app`.
   * - `.Analyzer`
     - `.HashDataStore`
     - (same as `.AnalysisApp`)

.. note:: `.Simulator` and `.Analyzer` have `.AutoDump` plugin which
   dumps the results of simulation or analysis to the datastore.  This
   is the main difference between `.Analyzer` and `.AnalysisApp`;
   i.e., `.AnalysisApp` does not save the result.

.. todo:: Then why I want to define both `.Analyzer` and `.AnalysisApp`?

.. todo:: How should I support "in-memory" datastore?
