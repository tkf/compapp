import numpy

from compapp import Computer, Plotter


class HistPlotter(Plotter):
    bins = 100

    def run(self, x):
        _, ax = self.figure.subplots()
        ax.hist(x, **self.params())


class CumHistPlotter(HistPlotter):
    cumulative = True


class MySimulator(Computer):
    samples = 1000

    def run(self):
        self.results.data = numpy.random.randn(self.samples)


class MyApp(Computer):
    sim = MySimulator
    density = HistPlotter
    cumdist = CumHistPlotter

    def run(self):
        self.sim.execute()
        self.density.execute(self.sim.results.data)
        self.cumdist.execute(self.sim.results.data)


if __name__ == '__main__':
    MyApp().execute()
