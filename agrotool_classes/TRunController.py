# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem, TAirPart
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
    def __init__(self, weatherList: TWeatherRecord):
        self.agroEcoSystem = TAgroEcoSystem(TAirPart())
        self.agroEcoSystem.RunController = self
        self.technologyDescriptor = TTechnologyDescriptor()
        self.weatherController = TWeatherController()
        self.measurementUnit = Measurements(0, 0, 0, 0)

        self.weatherList = weatherList
        self.currDay = 0
        self.agroEcoSystem.Air_Part.currentEnv = self.weatherList[self.currDay]

    def getCurrentDay(self):
        return self.weatherList[self.currDay]
