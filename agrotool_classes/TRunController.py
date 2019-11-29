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
        self.agroEcoSystem.Air_Part.currentEnv = self.weatherMap[self.currDay]
