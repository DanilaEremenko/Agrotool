import numpy as np
import matplotlib.pyplot as plt


class PlotContainer():
    def __init__(self, x=np.empty(0), y=np.empty(0), title="No title", divisor="-."):
        self.x = x
        self.y = y
        self.title = title
        self.divisor = divisor

    def append(self, x, y):
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)


class Plotter():
    @staticmethod
    def get_fig_and_splt(plt_container: PlotContainer):
        fig = plt.figure(dpi=200)
        splt = fig.add_subplot()
        splt.plot(plt_container.x, plt_container.y)
        splt.set_title(plt_container.title)

        return fig, splt

    @staticmethod
    def get_joined_figure(plt_containers_list):
        fig, axs = plt.subplots(len(plt_containers_list))
        for ax, splt in zip(axs, plt_containers_list):
            ax.plot(splt.x, splt.y, splt.divisor)
            ax.set_title(splt.title)

        return fig


# --------------------- example of using ---------------------------------------
if __name__ == '__main__':
    plt_containers = [
        PlotContainer([1, 2, 3, 4], [1, 2, 3, 4], "title1"),
        PlotContainer([4, 3, 2, 1], [1, 2, 3, 4], "title2")
    ]

    fig1, splt1 = Plotter.get_fig_and_splt(plt_containers[0])
    fig1.show()
    fig2, splt2 = Plotter.get_fig_and_splt(plt_containers[1])
    fig2.show()

    full_figure = Plotter.get_joined_figure(plt_containers_list=plt_containers)

    full_figure.show()
