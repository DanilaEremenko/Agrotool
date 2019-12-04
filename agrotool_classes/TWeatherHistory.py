import numpy as np
from agrotool_plotting.Plotter import Plotter, PlotContainer


class DayWeather():
    def __init__(self, tList=np.empty(0), radList=np.empty(0), deltaList=np.empty(0)):
        self.tList = tList
        self.radList = radList
        self.deltaList = deltaList

    def append(self, Rad, T, delta):
        self.radList = np.append(self.radList, Rad)
        self.tList = np.append(self.tList, T)
        self.deltaList = np.append(self.deltaList, delta)


class TWeatherHistory():
    def __init__(self):
        self.days_weather = {}

    def append_day(self, key, day: DayWeather):
        self.days_weather[key] = day

    def show_day(self, key):
        day_weather = self.days_weather[key]
        plt_containers = [
            PlotContainer(day_weather.deltaList, day_weather.radList, divisor='.', title="%d KHistory" % key),
            PlotContainer(day_weather.deltaList, day_weather.tList, divisor='.', title="%d THistory" % key)
        ]

        full_figure = Plotter.get_joined_figure(plt_containers_list=plt_containers)

        full_figure.show()

    def show_all_days(self):
        k_container = PlotContainer(title="Radiation history", divisor='.-',
                                    x_label="Day", y_label="K")
        t_container = PlotContainer(title="Full T history", divisor='.-',
                                    x_label="Day", y_label="T(°C)")
        time_shift = 0
        for day_num, day_weather in zip(self.days_weather.keys(), self.days_weather.values()):
            k_container.append(x=day_weather.deltaList + time_shift, y=day_weather.radList)
            t_container.append(x=day_weather.deltaList + time_shift, y=day_weather.tList)
            time_shift += 24
        full_figure, axs = Plotter.get_joined_figure(plt_containers_list=[t_container, k_container])

        # plotting dividing line after every day
        while (time_shift > 0):
            axs[0].plot((time_shift, time_shift), (0, 30), color='r')
            time_shift -= 24
        axs[0].set_ylim(min(t_container.y), max(t_container.y))

        full_figure.show()
