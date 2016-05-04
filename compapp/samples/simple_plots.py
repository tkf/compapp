from compapp.apps import Computer


class MyApp(Computer):

    def run(self):
        fig1 = self.figure()
        ax1 = fig1.add_subplot(111)
        ax1.plot([x ** 2 for x in range(100)])

        fig2, (ax21, ax22) = self.figure.subplots(2)
        ax21.plot([0, 2, 1, 3, 5])
        ax22.plot([0, 1, 5, 3, 0])

        # FIXME: a hack to show the figure in sphinx doc:
        self.figure.defer.callbacks.clear()


if __name__ == '__main__':
    MyApp().execute()
