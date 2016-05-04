from compapp import Computer


class PlottingApp(Computer):

    def run(self):
        fig = self.figure()
        ax = fig.add_axes(111)
        ax.plot([1, 2, -1, 5])


if __name__ == '__main__':
    app = PlottingApp.cli()
