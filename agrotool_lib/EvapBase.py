# TODO check functions
from agrotool_lib.DebugInspector import whoami
from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem
from agrotool_lib.HeatEquation import cn_diffusion_equation
import numpy as np


def evapo_transpiration(cSystem: TAgroEcoSystem):
    print("%s is a stub" % whoami())
    return 0


def soil_temperature(cSystem: TAgroEcoSystem, T_curr):
    cSystem.soil_part.calculate_temperature_in_layers()
    T_0 = np.zeros(len(cSystem.soil_part.soil_layers))
    D_arr = np.zeros(len(cSystem.soil_part.soil_layers))
    C_arr = np.zeros(len(cSystem.soil_part.soil_layers))

    for i, layer in enumerate(cSystem.soil_part.soil_layers):
        T_0[i] = layer.T
        D_arr[i] = layer.params.C * layer.params.D  # Это правильно
        C_arr[i] = layer.params.C

    T_0[0] = T_curr

    N = 10
    dx = cSystem.soil_part.soil_layers[0].dh
    dt = cSystem.run_controller.step_time_delta.seconds / N
    bc_val = [T_curr, cSystem.run_controller.region.T_AVG_YEAR]

    T, t = cn_diffusion_equation(
        T_0=T_0,
        D_arr=D_arr,
        C_arr=C_arr,
        dx=dx,
        dt=dt,
        N=N,
        bc_val=bc_val,
        bc_type=['val', 'val']
    )

    for T_new, layer in zip(T, cSystem.soil_part.soil_layers):
        layer.T = T_new[-1]
