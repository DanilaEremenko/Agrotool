# TODO check classes
from agrotool_lib.DebugInspector import whoami
from .TDate import TDate
import copy
import json


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

    @staticmethod
    def get_map_from_json(json_file):
        with open(json_file) as json_data:
            json_data = json.load(json_data)
        json_data = json_data["Weather"]
        weather_map = {}
        for key in json_data.keys():
            weather_map[int(key)] = TWeatherRecord(date=TDate(days=int(key)),
                                                   prec=json_data[key]["Prec"],
                                                   tmin=json_data[key]["Tmin"],
                                                   tmax=json_data[key]["Tmax"],
                                                   kex=json_data[key]["Kex"],
                                                   isSomething=False,
                                                   watering=0)  # TODO watering
        return weather_map


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
        self.sumSnow = 0  # TODO
        self.alpha_snow = 0
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
