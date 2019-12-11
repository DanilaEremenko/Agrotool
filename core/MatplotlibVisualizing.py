import matplotlib.pyplot as plt
import numpy as np


class PlotContainer():
    def __init__(self, x=np.empty(0), y=np.empty(0), title="No title", divisor="-/",
                 x_label="No label", y_label="No label"):
        self.x = x
        self.y = y
        self.title = title
        self.divisor = divisor
        self.x_label = x_label
        self.y_label = y_label

    def append(self, x, y):
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)


def get_fig_and_splt(plt_container: PlotContainer):
    fig = plt.figure(dpi=200)
    splt = fig.add_subplot()
    splt.plot(plt_container.x, plt_container.y)
    splt.set_title(plt_container.title)

    return fig, splt


def get_joined_figure(plt_containers_list):
    fig, axs = plt.subplots(len(plt_containers_list))
    for ax, splt in zip(axs, plt_containers_list):
        ax.plot(splt.x, splt.y, splt.divisor)
        ax.set_xlabel(splt.x_label)
        ax.set_ylabel(splt.y_label)
        ax.set_title(splt.title)

    return fig, axs


def show_all_days(weatherHistory):
    k_container = PlotContainer(title="Radiation history", divisor='.-',
                                x_label="Day", y_label="K")
    t_container = PlotContainer(title="Full T history", divisor='.-',
                                x_label="Day", y_label="T(°C)")
    prec_container = PlotContainer(title="Full Prec History", divisor='.-', x_label="Day", y_label="R(mm)")
    time_shift = 0
    for day_num, day_weather in zip(weatherHistory.days_weather.keys(), weatherHistory.days_weather.values()):
        t_container.append(x=day_weather.deltaList + time_shift, y=day_weather.tList)
        prec_container.append(x=day_weather.deltaList + time_shift, y=day_weather.precList)
        k_container.append(x=day_weather.deltaList + time_shift, y=day_weather.radList)
        time_shift += 24

    full_figure, axs = get_joined_figure(plt_containers_list=[t_container, prec_container, k_container])

    # plotting dividing line after every day
    while (time_shift > 0):
        axs[0].plot((time_shift, time_shift), (min(t_container.y), max(t_container.y)), color='r')
        axs[1].plot((time_shift, time_shift), (min(prec_container.y), max(prec_container.y)), color='r')
        axs[2].plot((time_shift, time_shift), (min(k_container.y), max(k_container.y)), color='r')

        time_shift -= 24
    axs[0].set_ylim(min(t_container.y), max(t_container.y))

    full_figure.show()


def show_day(weatherHistory, key):
    day_weather = weatherHistory.days_weather[key]
    plt_containers = [
        PlotContainer(day_weather.deltaList, day_weather.radList, divisor='.', title="%d KHistory" % key),
        PlotContainer(day_weather.deltaList, day_weather.tList, divisor='.', title="%d THistory" % key),
        PlotContainer(day_weather.deltaList, day_weather.precList, divisor='.', title="%d PrecHistory" % key)
    ]

    full_figure = get_joined_figure(plt_containers_list=plt_containers)

    full_figure.show()
