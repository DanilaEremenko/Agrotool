from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem
from agrotool_lib.PhysicalConstants import asn, bsn

from datetime import timedelta
import numpy as np


# TODO Using daily step?
def popov_melting(cSystem: TAgroEcoSystem, cDateTime, stepTimeDelta, TCurr):
    cWR = cSystem.Air_Part.currentEnv
    wind = cWR.wind
    cloud = (np.sqrt(1 - 8 * (cWR.Kex - asn - bsn) / bsn) - 1) / 2

    if cSystem.Air_Part.alpha_snow == 0:
        cSystem.Air_Part.alpha_snow = 0.4
    elif cSystem.Air_Part.alpha_snow < 1:
        cSystem.Air_Part.alpha_snow = cSystem.Air_Part.alpha_snow + 0.2 * stepTimeDelta.seconds / \
                                      (3600 * (timedelta(hours=24) / stepTimeDelta))

    CN = 1 + 0.24 * cloud

    if cDateTime.hour > 6 and cDateTime.hour < 18:
        sum_melt = 3.1 * cSystem.Air_Part.alpha_snow * (cWR.Tmax - cWR.Tave) + 0.675 * (
                CN * (TCurr + 45) - 60) + 0.83 * (1 + 0.54 * wind) * (TCurr - 0.65)
    else:
        sum_melt = 0.83 * (1 + 0.54 * wind) * (TCurr - 0.65) + 0.675 * (CN * (TCurr + 45) - 60)

    sum_melt *= stepTimeDelta.seconds / (3600 * (timedelta(hours=24) / stepTimeDelta))

    SumSnow = cSystem.Air_Part.SumSnow
    sum = max(sum_melt, 0)

    result = min(sum, SumSnow)
    print("popov return %d (must be checked)" % result)

    return result
