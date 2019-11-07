# TODO check classes

from .TRegimes import TIrrigation_Regime, TFertilization_Regime, TSoil_Tillage_Regime, THarvesting_Regime


class TTechnologyDescriptor():
    def __init__(self,
                 Irrigation_Regime=TIrrigation_Regime(),
                 Fertilization_Regime=TFertilization_Regime(),
                 Soil_Tillage_Regime=TSoil_Tillage_Regime(),
                 Harvesting_Regime=THarvesting_Regime()
                 ):
        self.Irrigation_Regime = Irrigation_Regime
        self.Fertilization_Regime = Fertilization_Regime
        self.Soil_Tillage_Regime = Soil_Tillage_Regime
        self.Harvesting_Regime = Harvesting_Regime
