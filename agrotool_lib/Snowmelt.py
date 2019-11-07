from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem
import numpy as np


def popov_melting(cSystem: TAgroEcoSystem):
    asn = bsn = 1  # TODO what are these constants?
    cWR = cSystem.Air_Part.currentEnv
    cs = "%d" % cWR.date
    Tave = cWR.Tave
    Tmax = cWR.Tmax
    Tmin = cWR.Tmin
    Tday = (Tmax + Tave) / 2
    Tnight = (Tmin + Tave) / 2
    wind = 4
    kex = cWR.Kex
    cloud = (np.sqrt(1 - 8 * (kex - asn - bsn) / bsn) - 1) / 2
    if cSystem.Air_Part.alpha_snow == 0:
        cSystem.Air_Part.alpha_snow = 0.4
    elif cSystem.Air_Part.alpha_snow < 1:
        cSystem.Air_Part.alpha_snow = cSystem.Air_Part.alpha_snow + 0.2

    CN = 1 + 0.24 * cloud
    sum_day = 3.1 * cSystem.Air_Part.alpha_snow * (Tmax - Tave) + 0.675 * (CN * (Tday + 45) - 60) + 0.83 * (
            1 + 0.54 * wind) * (Tday - 0.65)
    sum_night = 0.83 * (1 + 0.54 * wind) * (Tnight - 0.65) + 0.675 * (CN * (Tnight + 45) - 60)
    SumSnow = cSystem.Air_Part.sumSnow
    sum = max(sum_day + sum_night, 0)

    return min(sum, SumSnow)
