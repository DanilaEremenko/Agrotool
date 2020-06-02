# TODO check classes
import json

from .TAgroEcoSystem import TAgroEcoSystem, TAirPart, TWeatherRecord
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController
import pandas as pd
from datetime import timedelta, datetime


class Region():
    def __init__(self, latitude, slope_azimuth, slope_steepness, conc_CO2, avg_year_T):
        self.Latitude = latitude
        self.SlopeAzimuth = slope_azimuth
        self.SlopeSteepness = slope_steepness
        self.CO2Conc = conc_CO2
        self.T_AVG_YEAR = avg_year_T


class TRunController():
    def __init__(self, weatherPath, modelPath, placePath):
        # TODO refactor json format
        # TODO add json with intermediate measurement of weather
        self.weather_df = pd.DataFrame(self._parse_json(json_path=weatherPath, key='Weather'))

        # save string from json in datetime format
        self.weather_df['Date'] = pd.Series(
            list(
                map(lambda datestr: datetime.strptime(datestr, "%d/%m/%Y").strftime("%d/%m/%Y"),
                    self.weather_df['Date'])
            )
        )
        model_dict = self._parse_json(json_path=modelPath, key='MODEL_PARAMS')
        place_params = self._parse_json(json_path=placePath, key='Place')

        self.agro_eco_system = TAgroEcoSystem(
            airPart=TAirPart(),
            layers_num=model_dict['N_SOIL_LAYERS'],
            depth=model_dict['SOIL_DEPTH']
        )
        self.step_time_delta = timedelta(
            hours=model_dict['TIME_STEP']['HOURS'],
            minutes=model_dict['TIME_STEP']['MINUTES'],
            seconds=model_dict['TIME_STEP']['SECONDS']
        )
        self.agro_eco_system.run_controller = self
        self.technology_descriptor = TTechnologyDescriptor()
        self.weather_controller = TWeatherController()
        self.region = Region(
            latitude=place_params['Region']['LATITUDE'],
            slope_azimuth=place_params['Area']['SLOPE_AZIMUTH'],
            slope_steepness=place_params['Area']['SLOPE_STEEP'],
            conc_CO2=place_params['Region']['CO2Concentration'],
            avg_year_T=place_params['MeteoStation']['T_AVG_YEAR']

        )

        self.curr_day = 0
        self.agro_eco_system.air_part.currentEnv = TWeatherRecord(self.weather_df.to_dict(orient='records')[0])

    @staticmethod
    def _parse_json(json_path, key):
        with open(json_path) as json_fp:
            return json.load(json_fp)[key]

    def init_start(self, jsonPath):
        init_json = self._parse_json(json_path=jsonPath, key='InitialState')
        self.agro_eco_system.soil_part.init_start(T=init_json['Temperature'], W=init_json['WaterStorage'])

    def update_params(self, solid_path):
        # TODO add other systems
        self.agro_eco_system.soil_part.update_params(solid_path)

    def get_current_day(self):
        return self.weather_df[self.curr_day]
