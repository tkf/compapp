def import_object(name, current_module=None):
    """
    Import an object at "dotted path".

    >>> from importlib import import_module
    >>> import_object('importlib.import_module') is import_module
    True

    Any object such as package, module, sub-module, function and class
    can be imported:

    >>> import_object('json')                          # doctest: +ELLIPSIS
    <module 'json' from '...'>
    >>> import_object('json.load')                     # doctest: +ELLIPSIS
    <function load at ...>
    >>> import_object('os.path')                       # doctest: +ELLIPSIS
    <module ...>
    >>> import_object('os.path.join')                  # doctest: +ELLIPSIS
    <function ...join at ...>

    To support relative import, `current_module` has to be provided.
    Typically, it's ``__name__``.::

        import_object('spam.egg', __name__)

    """
    if '.' not in name:
        return __import__(name)
    else:
        if name.startswith('.'):
            name = current_module.rsplit('.', 1)[0] + name
        (modpath, objname) = name.rsplit('.', 1)
        module = __import__(modpath, fromlist=[objname])
        return getattr(module, objname)
