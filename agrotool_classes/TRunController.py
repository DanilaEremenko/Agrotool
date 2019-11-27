# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController
from .TAgroEcoSystem import TWeatherRecord


class TRunController():
    def __init__(self,
                 agroEcoSystem: TAgroEcoSystem,
                 technologyDescriptor: TTechnologyDescriptor,
                 weatherController: TWeatherController,
                 weatherMap: TWeatherRecord):
        self.agroEcoSystem = agroEcoSystem
        self.technologyDescriptor = technologyDescriptor
        self.weatherController = weatherController
        self.weatherMap = weatherMap
        self.currDay = list(self.weatherMap.keys())[0]
        self.currDay = next(iter(self.weatherMap.keys()))  # outputs 'foo'
        self.agroEcoSystem.Air_Part.currentEnv = self.get_curr_wr()

    def inc_day(self):
        self.currDay += 1

    def get_curr_wr(self):  # TODO replace with iter
        try:
            return self.weatherMap[self.currDay]
        except Exception:
            return None
