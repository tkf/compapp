=================
 Quick reference
=================

Core
====

.. currentmodule:: compapp.core

.. autosummary::

   compapp.core
   Parametric
   Parametric.params
   Parametric.paramnames
   Parametric.defaultparams


Executables
===========

.. currentmodule:: compapp.interface

.. autosummary::

   Executable
   Executable.prepare
   Executable.run
   Executable.save
   Executable.load
   Executable.finish
   Executable.execute

.. currentmodule:: compapp

.. autosummary::

   executables.Loader
   executables.Plotter
   apps
   apps.Computer
   apps.Computer.cli
   apps.Memoizer


Plugins
=======

.. currentmodule:: compapp.interface

.. autosummary::

   Plugin
   Plugin.prepare
   Plugin.pre_run
   Plugin.post_run
   Plugin.save
   Plugin.load
   Plugin.finish

`compapp.plugins`
-----------------

.. currentmodule:: compapp.plugins

.. autosummary::

   ~datastores.DirectoryDataStore
   ~datastores.SubDataStore
   ~datastores.HashDataStore
   ~metastore.MetaStore
   ~misc.Logger
   ~misc.Debug
   ~misc.Figure
   ~misc.AutoUpstreams
   ~recorders.DumpResults
   ~recorders.DumpParameters
   ~vcs.RecordVCS
   ~timing.RecordTiming
   ~programinfo.RecordProgramInfo
   ~sysinfo.RecordSysInfo


Descriptors
===========

.. currentmodule:: compapp.descriptors

.. autosummary::

   ~traits.OfType
   ~traits.Required
   ~traits.List
   ~traits.Dict
   ~traits.Optional
   ~traits.Choice
   ~traits.Or
   ~links.Link
   ~links.Root
   ~links.Delegate
   ~links.MyName
   ~links.OwnerName
   ~misc.Constant
   ~dynamic_class.dynamic_class
   ~dynamic_class.ClassPath
   ~dynamic_class.ClassPlaceholder


Utilities
=========

.. currentmodule:: compapp

.. autosummary::

   ~interactive.setup_interactive
