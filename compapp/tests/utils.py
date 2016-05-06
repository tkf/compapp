class DataChecker(object):

    def test(self):
        for data in self.data:
            assert isinstance(data, tuple)
            yield (self.check,) + data
