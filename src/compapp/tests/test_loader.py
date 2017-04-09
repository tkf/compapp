from .test_setters import MyApp, ClassB


def test_load_dynamic_class(tmpdir):
    app1 = MyApp()
    app1.datastore.dir = str(tmpdir)
    app1.classpath = '.ClassB'
    app1.execute()

    app2 = MyApp()
    app2.datastore.dir = str(tmpdir)
    app2.mode = 'load'
    app2.execute()

    assert app2.classpath == '.ClassB'
    assert isinstance(app2.dynamic, ClassB)
    assert app2.dynamic.x == ClassB.x
