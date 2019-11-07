# TODO check classes

from .TAgroEcoSystem import TAgroEcoSystem
from .TTechnologyDescriptor import TTechnologyDescriptor


class TRunController():
    def function_sdsd(self):
        pass

    def __init__(self, agroEcoSystem: TAgroEcoSystem,
                 technologyDescriptor: TTechnologyDescriptor,
                 weatherController):
        self.agroEcoSystem = agroEcoSystem
        self.technologyDescriptor = technologyDescriptor
        self.weatherController = weatherController
