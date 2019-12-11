# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem, TAirPart, TWeatherRecord
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController


class Measurements():
    def __init__(self, Latitude, SlopeAzimuth, SlopeSteepness, CO2Conc):
        self.Latitude = Latitude
        self.SlopeAzimuth = SlopeAzimuth
        self.SlopeSteepness = SlopeSteepness
        self.CO2Conc = CO2Conc


class TRunController():
    def __init__(self, weatherDf):
        self.agroEcoSystem = TAgroEcoSystem(TAirPart())
        self.agroEcoSystem.RunController = self
        self.technologyDescriptor = TTechnologyDescriptor()
        self.weatherController = TWeatherController()
        self.measurementUnit = Measurements(0, 0, 0, 0)

        self.weatherDf = weatherDf
        self.currDay = 0
        self.agroEcoSystem.Air_Part.currentEnv = TWeatherRecord(self.weatherDf.to_dict(orient='records')[0])

    def getCurrentDay(self):
        return self.weatherDf[self.currDay]
