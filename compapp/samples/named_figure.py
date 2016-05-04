import numpy

from compapp.apps import Computer


class MyApp(Computer):

    def run(self):
        names = ['a', 'b', 'c']

        for name in names:
            fig = self.figure(figsize=(2, 0.5), name=name)
            fig.add_subplot(111)

        for j in range(1, 5):
            for i, name in enumerate(names):
                x = numpy.zeros(100)
                x[(i + j) * 10 + 20] = j * 10
                self.figure[name].axes[0].plot(x)

        for name in names:
            ax = self.figure[name].axes[0]
            ax.set_yticks([0, 30])
            ax.text(10, 10, name)


if __name__ == '__main__':
    MyApp().execute()
