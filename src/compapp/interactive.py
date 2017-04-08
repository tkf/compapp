def setup_interactive():
    """
    Configure compapp for REPL (e.g., IPython).

    This function modify the default for compapp classes (only
    `.Figure`, at the moment) to behave nicely in REPLs.

    """
    from .plugins import Figure
    Figure.autoclose.default = False
