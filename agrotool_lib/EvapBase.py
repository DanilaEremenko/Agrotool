# TODO check functions
from agrotool_lib.DebugInspector import whoami
from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem
from agrotool_lib.HeatEquation import CN_diffusion_equation
import numpy as np


def Evapotranspiration(cSystem: TAgroEcoSystem):
    print("%s is a stub" % whoami())
    return 0


def SoilTemperature(cSystem: TAgroEcoSystem, T_curr):
    cSystem.soilPart.calculate_temperature_in_layers()
    T_0 = np.zeros(len(cSystem.soilPart.soilLayers))
    D_arr = np.zeros(len(cSystem.soilPart.soilLayers))
    C_arr = np.zeros(len(cSystem.soilPart.soilLayers))

    for i, layer in enumerate(cSystem.soilPart.soilLayers):
        T_0[i] = layer.T
        D_arr[i] = layer.D
        C_arr[i] = layer.C

    N = 10
    dx = cSystem.soilPart.soilLayers[0].dh
    dt = cSystem.runController.stepTimeDelta.seconds / N
    bc_val = [T_curr, cSystem.runController.region.T_AVG_YEAR]

    T, t = CN_diffusion_equation(
        T_0=T_0,
        D_arr=D_arr,
        C_arr=C_arr,
        dx=dx,
        dt=dt,
        N=N,
        bc_val=bc_val,
        bc_type=['val', 'val']
    )

    for T_curr, layer in zip(T, cSystem.soilPart.soilLayers):
        layer.T = T_curr[-1]
