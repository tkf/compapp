from ..apps import Computer


class NoOp(Computer):
    class sub(Computer):
        class sub(Computer):
            class sub(Computer):
                pass


def test_nested_empty_computer():
    app = NoOp()
    app.execute()
