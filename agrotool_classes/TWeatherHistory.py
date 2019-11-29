import numpy as np
from agrotool_plotting.Plotter import Plotter, PlotContainer


class DayWeather():
    def __init__(self, tList=np.empty(0), kList=np.empty(0), deltaList=np.empty(0)):
        self.tList = tList
        self.kList = kList
        self.deltaList = deltaList

    def append(self, Kex, T, delta):
        self.kList = np.append(self.kList, Kex)
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
            PlotContainer(day_weather.kList, day_weather.deltaList, divisor='.', title="%d KHistory" % key),
            PlotContainer(day_weather.tList, day_weather.deltaList, divisor='.', title="%d THistory" % key)
        ]

        full_figure = Plotter.get_joined_figure(plt_containers_list=plt_containers)

        full_figure.show()