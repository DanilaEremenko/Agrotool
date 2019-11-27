# TODO check classes
from agrotool_lib.DebugInspector import whoami
from .TDate import TDate
import copy


class TWeatherRecord():
    def __init__(self, date: TDate, prec, watering, tmin, tmax, kex, isSomething):
        self.date = date
        self.Prec = prec  # precipitation
        self.Watering = watering
        self.Tmin = tmin  # min temperature
        self.Tmax = tmax  # max temperature
        self.Tave = int((self.Tmax + self.Tmin) / 2)  # average temperature
        self.Kex = kex  # ослабление солнечной радиации (облачность фактическая радиация/если бы не было облаков)
        # TODO RadiationAstronomy._DayLength

    def __copy__(self):
        return copy.deepcopy(self)


# ------------------------------- Environment parts --------------------------------------------
class TAirPart():
    def __init__(self, currentEnv: TWeatherRecord):
        self.currentEnv = currentEnv
        self.sumSnow = 100  # TODO
        self.alpha_snow = 0
        self.sumTrans = 0
        self.sumPrec = 0


class TIndividualtPlant():
    def __init__(self):
        self.Ifase = 0
        self.Ph_Time = 0


class TCrop_Part():
    def __init__(self):
        self.Esoil = 0
        self.Eplant = 0
        self.Individual_Plant = TIndividualtPlant()


# 10 parts
class TSoil_Part():
    def __init__(self):
        pass


# ------------------------------- AgroEcoSystem --------------------------------------------
class TAgroEcoSystem():
    def __init__(self, Air_Part: TAirPart):
        self.Air_Part = Air_Part
        self.Crop_Part = TCrop_Part()
        self.Soil_Part = TSoil_Part()

    def refreshing(self):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
        pass
