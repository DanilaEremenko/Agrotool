# TODO check classes
import json

from agrotool_lib import ThIdent
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
        self.prec = data["Prec"]  # precipitation
        self.wind = data["Wind"]
        self.watering = 0  # TODO ???
        self.temp_min = data["Tmin"]  # min temperature
        self.temp_max = data["Tmax"]  # max temperature
        self.temp_avg = int((self.temp_max + self.temp_min) / 2)  # average temperature
        self.kex = data[
            "Kex"]  # ослабление солнечной радиации (облачность фактическая радиация/если бы не было облаков)

    def __copy__(self):
        return copy.deepcopy(self)


###########################################################################################
# ------------------------------- Culture part --------------------------------------------
###########################################################################################
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


##########################################################################################
# ------------------------------- Plant parts --------------------------------------------
##########################################################################################
class TPlantPart():
    def __init__(self):
        self.area_index = 0


class TStem(TPlantPart):
    def __init__(self):
        super().__init__()


class TLeaf(TPlantPart):
    def __init__(self):
        super().__init__()
        self.res_stom = 0
        self.lai = 0


class TShoot():
    def __init__(self):
        self.leaf = TLeaf()
        self.stem = TStem()


class TIndividualtPlant():
    def __init__(self):
        self.ifase = 0
        self.ph_time = 0
        self.shoot = TShoot()
        self.culture_descriptor = Culture()


##########################################################################################
# ------------------------------- Environment parts --------------------------------------
##########################################################################################

# ------------------ Air --------------------------
class TAirPart():
    def __init__(self):
        self.sum_snow = 0  # TODO
        self.alpha_snow = 0  # ready for melting
        self.sum_trans = 0
        self.sum_prec = 0
        self.sum_rad = 0
        self.Rnl = 0
        self.Rn = 0
        self.G = 0

    def setBalanceParams(self, Rnl, Rn, G):
        self.Rnl = Rnl
        self.Rn = Rn
        self.G = G


# ------------------ Crop --------------------------
class TCropPart():
    def __init__(self):
        self.esoil = 0
        self.eplant = 0
        self.rsh_plant = 0
        self.copr = 0
        self.individual_plant = TIndividualtPlant()


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
        self.C = 0
        self.D = 0

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
        res, is_okay = ThIdent.identify(
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
        self.soil_surface = TSoilSurface()
        self.soil_layers = []
        dh = depth / layers_num
        h = 0
        for i in range(layers_num):
            self.soil_layers.append(TSoiltLayer(T=0, W=0, dh=dh, h=h))
            h += dh

    def calculate_temperature_in_layers(self):
        # TODO
        for layer in self.soil_layers:
            layer.calculate_termo_params()

    def init_start(self, T, W):
        for layer in self.soil_layers:
            layer.T = T
            layer.W = W / 100

    @staticmethod
    def read_soil_file(path_solid, format='ISRIC'):
        # ISRIC,ICASA
        with open(path_solid) as solid_fp:
            solid_dict = json.load(solid_fp)

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
        for layer in self.soil_layers:

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

        for i, layer in enumerate(self.soil_layers):
            layer.params.update(new_df.iloc[i])


##########################################################################################
# ------------------------------- AgroEcoSystem ------------------------------------------
##########################################################################################
class TAgroEcoSystem():
    def __init__(self, airPart: TAirPart, layers_num, depth):
        self.air_part = airPart
        self.crop_part = TCropPart()
        self.soil_part = TSoilPart(layers_num, depth)
        self.run_controller = None

    def refreshing(self):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
        pass
