from contextlib import contextmanager
import os
import tempfile


@contextmanager
def safewrite(path, mode='w'):
    """
    Open a temporary file and replace it with `path` upon close.

    Examples
    --------

    .. Run the code below in a clean temporary directory:
       >>> getfixture('cleancwd')

    >>> with open('data.txt', 'w') as f:
    ...     _ = f.write('original content')
    >>> with safewrite('data.txt') as f:
    ...     _ = f.write(str(1 / 0))                    # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    ZeroDivisionError: ...
    >>> with open('data.txt') as f:
    ...     print(f.read())
    original content

    If it were a normal `open`, then the original content would be
    wiped out.

    >>> with open('data.txt', 'w') as f:
    ...     _ = f.write(str(1 / 0))                    # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    ZeroDivisionError: ...
    >>> with open('data.txt') as f:
    ...     print(f.read())
    <BLANKLINE>

    """
    abspath = os.path.abspath(path)
    base = os.path.basename(abspath)
    dir = os.path.dirname(abspath)
    try:
        with tempfile.NamedTemporaryFile(mode=mode, prefix=base, dir=dir,
                                         delete=False) as tmpf:
            yield tmpf
            os.rename(tmpf.name, abspath)
    finally:
        if os.path.exists(tmpf.name):
            os.unlink(tmpf.name)
