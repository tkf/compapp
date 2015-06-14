from compapp import SimulationApp


class SimpleApp(SimulationApp):

    x = 1.0
    y = 2.0
    retuls_names = ['the_sum']

    def run(self):
        self.the_sum = self.x + self.y


if __name__ == '__main__':
    app = SimpleApp.cli()
