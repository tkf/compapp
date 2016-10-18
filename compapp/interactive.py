def setup_interactive():
    from .plugins import Figure
    Figure.autoclose.default = False
