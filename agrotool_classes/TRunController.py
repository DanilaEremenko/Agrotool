# TODO check classes
import json

from .TAgroEcoSystem import TAgroEcoSystem, TAirPart, TWeatherRecord
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController
import pandas as pd
from datetime import timedelta, datetime


class Region():
    def __init__(self, Latitude, SlopeAzimuth, SlopeSteepness, CO2Conc, T_AVG_YEAR):
        self.Latitude = Latitude
        self.SlopeAzimuth = SlopeAzimuth
        self.SlopeSteepness = SlopeSteepness
        self.CO2Conc = CO2Conc
        self.T_AVG_YEAR = T_AVG_YEAR


class TRunController():
    def _parse_json(self, json_path, key):
        with open(json_path) as json_fp:
            return json.load(json_fp)[key]

    def __init__(self, weatherPath, modelPath, placePath):
        # TODO refactor json format
        # TODO add json with intermediate measurement of weather
        self.weatherDf = pd.DataFrame(self._parse_json(json_path=weatherPath, key='Weather'))

        # save string from json in datetime format
        self.weatherDf['Date'] = pd.Series(
            list(
                map(lambda datestr: datetime.strptime(datestr, "%d/%m/%Y").strftime("%d/%m/%Y"), self.weatherDf['Date'])
            )
        )
        modelDict = self._parse_json(json_path=modelPath, key='MODEL_PARAMS')
        placeParams = self._parse_json(json_path=placePath, key='Place')

        self.agroEcoSystem = TAgroEcoSystem(
            airPart=TAirPart(),
            layers_num=modelDict['N_SOIL_LAYERS'],
            depth=modelDict['SOIL_DEPTH']
        )
        self.stepTimeDelta = timedelta(
            hours=modelDict['TIME_STEP']['HOURS'],
            minutes=modelDict['TIME_STEP']['MINUTES'],
            seconds=modelDict['TIME_STEP']['SECONDS']
        )
        self.agroEcoSystem.runController = self
        self.technologyDescriptor = TTechnologyDescriptor()
        self.weatherController = TWeatherController()
        self.region = Region(
            Latitude=placeParams['Region']['LATITUDE'],
            SlopeAzimuth=placeParams['Area']['SLOPE_AZIMUTH'],
            SlopeSteepness=placeParams['Area']['SLOPE_STEEP'],
            CO2Conc=placeParams['Region']['CO2Concentration'],
            T_AVG_YEAR=placeParams['MeteoStation']['T_AVG_YEAR']

        )

        self.currDay = 0
        self.agroEcoSystem.airPart.currentEnv = TWeatherRecord(self.weatherDf.to_dict(orient='records')[0])

    def init_start(self, jsonPath):
        init_json = self._parse_json(json_path=jsonPath, key='InitialState')
        self.agroEcoSystem.soilPart.init_start(T=init_json['Temperature'], W=init_json['WaterStorage'])

    def update_params(self, solid_path):
        # TODO add other systems
        self.agroEcoSystem.soilPart.update_params(solid_path)

    def getCurrentDay(self):
        return self.weatherDf[self.currDay]
