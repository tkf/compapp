from compapp import Computer


class SimpleApp(Computer):

    x = 1.0
    y = 2.0

    def run(self):
        self.results.sum = self.x + self.y


if __name__ == '__main__':
    app = SimpleApp.cli()
