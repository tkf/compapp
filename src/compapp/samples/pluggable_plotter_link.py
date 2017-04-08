import numpy

from compapp import Computer, Plotter, Link, AutoUpstreams


class HistPlotter(Plotter):
    bins = 100
    data = Link('..sim.results.data')

    def run(self):
        _, ax = self.figure.subplots()
        ax.hist(self.data, **self.params())


class CumHistPlotter(HistPlotter):
    cumulative = True


class MySimulator(Computer):
    samples = 1000

    def run(self):
        self.results.data = numpy.random.randn(self.samples)


class MyApp(Computer):
    autoupstreams = AutoUpstreams
    sim = MySimulator
    density = HistPlotter
    cumdist = CumHistPlotter


if __name__ == '__main__':
    MyApp().execute()
