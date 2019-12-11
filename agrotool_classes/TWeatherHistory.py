import numpy as np
from core.MatplotlibVisualizing import PlotContainer
import pandas as pd


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
        self.pd_frame = pd.DataFrame(
            {"Date": np.empty(0), "T": np.empty(0), "Rad": np.empty(0), "Prec": np.empty(0)})

    def append_day(self, key, day: DayWeather):
        self.days_weather[key] = day

    def append_frame(self, new_frame_dict):
        self.pd_frame = self.pd_frame.append(pd.DataFrame(new_frame_dict))
