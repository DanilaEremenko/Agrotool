# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController
from .TAgroEcoSystem import TWeatherRecord


class Measurements():
    def __init__(self, Latitude, SlopeAzimuth, SlopeSteepness, CO2Conc):
        self.Latitude = Latitude
        self.SlopeAzimuth = SlopeAzimuth
        self.SlopeSteepness = SlopeSteepness
        self.CO2Conc = CO2Conc


class TRunController():
    def __init__(self,
                 agroEcoSystem: TAgroEcoSystem,
                 technologyDescriptor: TTechnologyDescriptor,
                 weatherController: TWeatherController,
                 weatherMap: TWeatherRecord,
                 measurementUnit: Measurements):
        self.agroEcoSystem = agroEcoSystem
        self.agroEcoSystem.RunController = self
        self.technologyDescriptor = technologyDescriptor
        self.weatherController = weatherController
        self.weatherMap = weatherMap
        self.currDay = list(self.weatherMap.keys())[0]
        self.agroEcoSystem.Air_Part.currentEnv = self.weatherMap[self.currDay]
        self.measurementUnit = measurementUnit

    def getCurrentDay(self):
        return self.weatherMap[self.currDay]
