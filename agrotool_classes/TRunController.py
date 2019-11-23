# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem
from .TTechnologyDescriptor import TTechnologyDescriptor
from .TWeatherController import TWeatherController


class TRunController():
    def __init__(self, agroEcoSystem: TAgroEcoSystem,
                 technologyDescriptor: TTechnologyDescriptor,
                 weatherController: TWeatherController):
        self.agroEcoSystem = agroEcoSystem
        self.technologyDescriptor = technologyDescriptor
        self.weatherController = weatherController
