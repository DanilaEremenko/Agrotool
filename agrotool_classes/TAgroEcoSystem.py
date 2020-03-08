# TODO check classes
import json

from agrotool_lib import thIdent
from agrotool_lib.DebugInspector import whoami
import copy
from datetime import datetime
import math
import pandas as pd
import numpy as np

from agrotool_mappings.SoilTextureTriangle import get_texture_by_conc, get_info_by_texture
from agrotool_mappings.USDA_mapping import get_params_dict_by_texture


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

        # soil
        self.K0 = 0
        self.W0 = 0
        self.A = 0
        self.B = 0
        self.C1 = 0
        self.C2 = 0

        # water
        self.Wfc = 0  # полевая влагоемкость
        self.Wz = 0  # влажность завядния
        self.tet_min = 0  # наименьшая влагоемкость
        self.tet_max = 0  # наибольшая влагоемкость (пористость)
        self.alpha_1 = 0  #
        self.beta_1 = 0
        self.beta_2 = 0
        self.Kf = 0  # базовый коэффициент филтрации

    def update_termo(self, res):
        self.K0 = res[1] * 1E-7
        self.W0 = res[2]
        self.A = res[3] * 1E-7
        self.B = res[4]
        self.C1 = res[5]
        self.C2 = res[6]

        if self.W0 == 0:
            print()
        if self.B == 0:
            print()

        self.C = 0
        self.D = 0

    def update_water(self, texture):
        params_dict = get_params_dict_by_texture(texture)

        self.Wfc = params_dict['Fc']
        self.tet_min = params_dict['Tr']
        self.tet_max = params_dict['Ts']
        self.Kf = params_dict['Kf']
        self.alpha_1 = params_dict['Alpha1']
        self.beta_1 = params_dict['Beta1']
        self.beta_2 = params_dict['Beta2']
        self.Wz = params_dict['Wz']

    def update(self, layer_params_df):
        texture = layer_params_df['Texture']
        if texture is None:
            texture, textType = get_texture_by_conc(sand=layer_params_df['Sand'],
                                                    silt=layer_params_df['Silt'],
                                                    clay=layer_params_df['Clay'])
        else:
            textType = get_info_by_texture(texture)['textType']

        print("texture = %s (sand = %.2f, silt = %.2f, clay = %.2f)" % (texture,
                                                                        layer_params_df['Sand'],
                                                                        layer_params_df['Silt'],
                                                                        layer_params_df['Clay']))

        # TODO replace with new realization
        res, is_okay = thIdent.identify(
            textType=textType,
            sand=layer_params_df['Sand'],
            silt=layer_params_df['Silt'],
            clay=layer_params_df['Clay'],
            bd=layer_params_df['Bd'],
            cc=layer_params_df['Corg']
        )

        self.update_termo(res)
        self.update_water(texture)


class TSoiltLayer():
    """
    TODO add description of class fields
    """

    def __init__(self, T, W, dh, h):
        self.T = T
        self.W = W
        self.dh = dh
        self.h = h
        self.rep_h = h + dh / 2
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

    def read_soil_file(self, path_solid, format='ISRIC'):
        # ISRIC,ICASA
        with open(path_solid) as solid_fp:
            solid_dict = json.load(solid_fp)

        tab_len = len(solid_dict['properties']['CLYPPT']['M'].values())
        return pd.DataFrame(
            {
                # TODO bad case if no top layer
                'Depth': np.array([20, 25, 35, 40, 60, 61, 62]) / 100,
                # 'Depth': np.array([0, 5, 15, 30, 60, 100, 200]) / 100,
                'Texture': [None, None, None, None, None, None, None],
                'Bd': list(solid_dict['properties']['BLDFIE']['M'].values()),
                'Corg': list(solid_dict['properties']['ORCDRC']['M'].values()),
                'Sand': list(solid_dict['properties']['SNDPPT']['M'].values()),
                'Silt': list(solid_dict['properties']['SLTPPT']['M'].values()),
                'Clay': list(solid_dict['properties']['CLYPPT']['M'].values()),
                'Wz': list(solid_dict['properties']['WWP']['M'].values()),
                'Fc': [None, None, None, None, None, None, None]
            }
        )

    def prepare_soil_layer_data(self, df):
        def _get_param(key, layer, is_str=True):

            # None layers processing
            if bottom_layer is None and top_layer is None:
                raise Exception("No neighbour layers")
            elif bottom_layer is None:
                return top_layer.iloc[0][key]
            elif top_layer is None:
                return bottom_layer.iloc[0][key]

            # df layers processing
            if bottom_layer.iloc[0][key] is None and bottom_layer.iloc[0][key] is None:
                return None
            elif bottom_layer.iloc[0][key] is None:
                return top_layer.iloc[key]
            elif bottom_layer.iloc[0][key] is None:
                return bottom_layer.iloc[key]

            # str processing
            elif is_str:
                if abs(bottom_layer['Depth'] - layer.rep_h) < abs(top_layer['Depth'] - layer.rep_h):
                    return bottom_layer[key]
                else:
                    return top_layer[key]

            # have all that we need processing
            else:
                return (bottom_layer.iloc[0][key] * (layer.rep_h - top_layer.iloc[0]['Depth']) +
                        top_layer.iloc[0][key] * (bottom_layer.iloc[0]['Depth'] - layer.rep_h)) / \
                       (bottom_layer.iloc[0]['Depth'] - top_layer.iloc[0]['Depth'])

        df = pd.DataFrame(df)
        df = df.drop(df[df['Depth'] < 0.07][df['Bd'] < 1000].index)

        new_dict = {'Depth': [], 'Texture': [], 'Bd': [], 'Corg': [], 'Sand': [], 'Silt': [], 'Clay': [], 'Wz': [],
                    'Fc': []}
        for layer in self.soilLayers:

            # define top layer
            top_layer = df[df['Depth'] <= layer.rep_h]
            if not top_layer.empty:
                top_layer = top_layer[top_layer['Depth'] == max(top_layer['Depth'])]
            else:
                top_layer = None

            # define bottom layer
            bottom_layer = df[df['Depth'] > layer.rep_h]
            if not bottom_layer.empty:
                bottom_layer = bottom_layer[bottom_layer['Depth'] == min(bottom_layer['Depth'])]
            else:
                bottom_layer = None

            # define out layer
            new_dict['Depth'].append(layer.rep_h)
            new_dict['Texture'].append(_get_param('Texture', layer, True))
            for key in ('Bd', 'Corg', 'Sand', 'Silt', 'Clay', 'Wz', 'Fc'):
                new_dict[key].append(_get_param(key, layer, False))

        return pd.DataFrame(new_dict)

    def update_params(self, solid_path):
        df = self.read_soil_file(solid_path)
        new_df = self.prepare_soil_layer_data(df)

        for i, layer in enumerate(self.soilLayers):
            layer.params.update(new_df.iloc[i])


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
