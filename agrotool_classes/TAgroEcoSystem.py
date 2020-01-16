# TODO check classes
from agrotool_lib.DebugInspector import whoami
import copy
from datetime import datetime


class TWeatherRecord():
    def __init__(self, data):
        self.date = datetime.strptime(data["Date"], "%d/%m/%Y")
        self.Prec = data["Prec"]  # precipitation
        self.wind = data["Wind"]
        self.Watering = 0  # TODO ???
        self.Tmin = data["Tmin"]  # min temperature
        self.Tmax = data["Tmax"]  # max temperature
        self.Tave = int((self.Tmax + self.Tmin) / 2)  # average temperature
        self.Kex = data[
            "Kex"]  # ослабление солнечной радиации (облачность фактическая радиация/если бы не было облаков)

    def __copy__(self):
        return copy.deepcopy(self)


# ------------------------------- Culture part --------------------------------------------
class Photosynthesis():
    def __init__(self):
        self.ResMes = 0
        self.PHMax = 0
        self.CExpen = 0
        self.alpha = 0
        self.Rx = 0


class Culture():
    def __init__(self):
        self.Photosynthesis_Type_Descriptor = Photosynthesis()


# ------------------------------- Plant parts --------------------------------------------
class TPlantPart():
    def __init__(self):
        self.AreaIndex = 0


class TStem(TPlantPart):
    def __init__(self):
        super().__init__()


class TLeaf(TPlantPart):
    def __init__(self):
        super().__init__()
        self.ResStom = 0


class TShoot():
    def __init__(self):
        self.Leaf = TLeaf()
        self.Stem = TStem()


class TIndividualtPlant():
    def __init__(self):
        self.Ifase = 0
        self.Ph_Time = 0
        self.Shoot = TShoot()
        self.Culture_Descriptor = Culture()


# ------------------------------- Environment parts --------------------------------------------
class TAirPart():
    def __init__(self):
        self.SumSnow = 0  # TODO
        self.alpha_snow = 0  # ready for melting
        self.sumTrans = 0
        self.sumPrec = 0
        self.SumRad = 0


class TCrop_Part():
    def __init__(self):
        self.Esoil = 0
        self.Eplant = 0
        self.RshPlant = 0
        self.copr = 0
        self.Individual_Plant = TIndividualtPlant()


class TSoilSurface():
    def __init__(self):
        pass


# 10 parts
class TSoil_Part():
    def __init__(self):
        self.SoilSurface = TSoilSurface()
        pass


# ------------------------------- AgroEcoSystem --------------------------------------------
class TAgroEcoSystem():
    def __init__(self, Air_Part: TAirPart):
        self.Air_Part = Air_Part
        self.Crop_Part = TCrop_Part()
        self.Soil_Part = TSoil_Part()
        self.RunController = None

    def refreshing(self):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
        pass
