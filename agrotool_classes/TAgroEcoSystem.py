# TODO check classes
from agrotool_lib.DebugInspector import whoami
import copy
from datetime import datetime
import math


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
# ------------------ Air --------------------------
class TAirPart():
    def __init__(self):
        self.SumSnow = 0  # TODO
        self.alpha_snow = 0  # ready for melting
        self.sumTrans = 0
        self.sumPrec = 0
        self.SumRad = 0


# ------------------ Crop --------------------------
class TCropPart():
    def __init__(self):
        self.Esoil = 0
        self.Eplant = 0
        self.RshPlant = 0
        self.copr = 0
        self.Individual_Plant = TIndividualtPlant()


# ------------------ Soil --------------------------
class TSoilSurface():
    def __init__(self):
        pass


class TLayerParams():
    def __init__(self):
        self.K0 = 0
        self.W0 = 0
        self.A = 0
        self.B = 0
        self.C1 = 0
        self.C2 = 0
        self.Wfc = 0

    def update(self):
        # TODO these params should be calculated
        self.K0 = 1.8E-7
        self.W0 = 0.31
        self.A = 2.7E-7
        self.B = 0.16
        self.C1 = 1.22E6
        self.C2 = 4.17E6
        self.Wfc = 0.45
        self.C = 0
        self.D = 0


class TSoiltLayer():
    """
    TODO add description of class fields
    """

    def __init__(self, T, W, dh, h):
        self.T = T
        self.W = W
        self.dh = dh
        self.h = h
        self.params = TLayerParams()

    def calculate_termo_params(self):
        self.params.C = self.params.C1 + self.params.C2 * self.W

        # K0 + A * exp(-0.5 * sqr(ln(W / W0) / B))
        self.params.D = self.params.K0 \
                        + self.params.A \
                        * math.exp(-0.5 * ((math.log(self.W / self.params.W0) / self.params.B) ** 2))


class TSoilPart():
    def __init__(self, layers_num, depth):
        self.soilSurface = TSoilSurface()
        self.soilLayers = []
        dh = depth / layers_num
        h = 0
        for i in range(layers_num):
            self.soilLayers.append(TSoiltLayer(T=0, W=0, dh=dh, h=h))
            h += dh

    def calculate_temperature_in_layers(self):
        # TODO
        for layer in self.soilLayers:
            layer.calculate_termo_params()

    def init_start(self, T, W):
        for layer in self.soilLayers:
            layer.T = T
            layer.W = W / 100

    def update_params(self):
        for layer in self.soilLayers:
            layer.params.update()


# ------------------------------- AgroEcoSystem --------------------------------------------
class TAgroEcoSystem():
    def __init__(self, airPart: TAirPart, layers_num, depth):
        self.airPart = airPart
        self.cropPart = TCropPart()
        self.soilPart = TSoilPart(layers_num, depth)
        self.runController = None

    def refreshing(self):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
        pass
