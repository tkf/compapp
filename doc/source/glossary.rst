============
 Glossaries
============

.. glossary::

   datastore

     Datastore is the directory to put your simulation and analysis
     results.  compapp may support more advanced data storage (e.g.,
     data bases) in the future.  See also `datastore
     <compapp.apps.Computer.datastore>` property.

   nested class
   owner class
   owner app

     Schematically,::

        class SubSimulator:
            pass

        class MySimulator:        # owns SubSimulator
            sub = SubSimulator    # nests in SubSimulator

        class MyApp:              # owns MySimulator
            sim = MySimulator     # nests in MyApp

     In the above example:

     - `MyApp` is the owner class of `MySimulator`.
     - `MySimulator` is the owner class of `SubSimulator`.

     In turn:

     - `SubSimulator` is a nested class of `MySimulator`.
     - `MySimulator` is a nested class of `MyApp`.

     An owner class happened to be a subclass of `.Computer` is
     called an *owner app*.

     (Side note: the term *owner* is from the interface of Python
     :term:`descriptor`; the `object.__get__` method receives the
     owner class as its last argument.)

   TBE
   to be extended

     Methods and properties marked as *to be extended* or *TBE* may be
     overridden (extended) by user-defined subclasses to implement
     certain functionalities.  Note that the override is completely
     optional as oppose to abstract methods and properties which are
     required to be overridden by subclasses.  In Python code,
     docstrings for such methods and properties are prefixed with
     ``|TO BE EXTENDED|``.

   composition over inheritance

     See: `Composition over inheritance - Wikipedia
     <https://en.wikipedia.org/wiki/Composition_over_inheritance>`_
