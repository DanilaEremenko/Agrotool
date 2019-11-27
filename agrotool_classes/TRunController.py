# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController
from .TAgroEcoSystem import TWeatherRecord


class TRunController():
    def __init__(self, agroEcoSystem: TAgroEcoSystem,
                 technologyDescriptor: TTechnologyDescriptor,
                 weatherController: TWeatherController,
                 currentEnv: TWeatherRecord):
        self.agroEcoSystem = agroEcoSystem
        self.technologyDescriptor = technologyDescriptor
        self.weatherController = weatherController
        self.currentEnv = currentEnv
