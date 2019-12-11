import numpy as np
from agrotool_plotting.Plotter import Plotter, PlotContainer


class DayWeather():
    def __init__(self, tList=np.empty(0), radList=np.empty(0), precList=np.empty(0), deltaList=np.empty(0)):
        self.tList = tList
        self.radList = radList
        self.precList = precList
        self.deltaList = deltaList

    def append(self, Rad, T, prec, delta):
        self.radList = np.append(self.radList, Rad)
        self.tList = np.append(self.tList, T)
        self.precList = np.append(self.precList, prec)
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
            PlotContainer(day_weather.deltaList, day_weather.tList, divisor='.', title="%d THistory" % key),
            PlotContainer(day_weather.deltaList, day_weather.precList, divisor='.', title="%d PrecHistory" % key)
        ]

        full_figure = Plotter.get_joined_figure(plt_containers_list=plt_containers)

        full_figure.show()

    def show_all_days(self):
        k_container = PlotContainer(title="Radiation history", divisor='.-',
                                    x_label="Day", y_label="K")
        t_container = PlotContainer(title="Full T history", divisor='.-',
                                    x_label="Day", y_label="T(°C)")
        prec_container = PlotContainer(title="Full Prec History", divisor='.-', x_label="Day", y_label="R(mm)")
        time_shift = 0
        for day_num, day_weather in zip(self.days_weather.keys(), self.days_weather.values()):
            t_container.append(x=day_weather.deltaList + time_shift, y=day_weather.tList)
            prec_container.append(x=day_weather.deltaList + time_shift, y=day_weather.precList)
            k_container.append(x=day_weather.deltaList + time_shift, y=day_weather.radList)
            time_shift += 24

        full_figure, axs = Plotter.get_joined_figure(plt_containers_list=[t_container, prec_container, k_container])

        # plotting dividing line after every day
        while (time_shift > 0):
            axs[0].plot((time_shift, time_shift), (min(t_container.y), max(t_container.y)), color='r')
            axs[1].plot((time_shift, time_shift), (min(prec_container.y), max(prec_container.y)), color='r')
            axs[2].plot((time_shift, time_shift), (min(k_container.y), max(k_container.y)), color='r')

            time_shift -= 24
        axs[0].set_ylim(min(t_container.y), max(t_container.y))

        full_figure.show()
