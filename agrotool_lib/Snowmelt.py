from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem
from agrotool_lib.PhysicalConstants import asn, bsn

from datetime import timedelta
import numpy as np


# TODO Using daily step?
def popov_melting(c_system: TAgroEcoSystem, c_date_time, step_time_delta, TCurr):
    cWR = c_system.air_part.currentEnv
    wind = cWR.wind
    cloud = (np.sqrt(1 - 8 * (cWR.kex - asn - bsn) / bsn) - 1) / 2

    if c_system.air_part.alpha_snow == 0:
        c_system.air_part.alpha_snow = 0.4
    elif c_system.air_part.alpha_snow < 1:
        c_system.air_part.alpha_snow = c_system.air_part.alpha_snow + 0.2 * step_time_delta.seconds / \
                                       (3600 * (timedelta(hours=24) / step_time_delta))

    CN = 1 + 0.24 * cloud

    if 6 < c_date_time.hour < 18:
        sum_melt = 3.1 * c_system.air_part.alpha_snow * (cWR.temp_max - cWR.temp_avg) + 0.675 * (
                CN * (TCurr + 45) - 60) + 0.83 * (1 + 0.54 * wind) * (TCurr - 0.65)
    else:
        sum_melt = 0.83 * (1 + 0.54 * wind) * (TCurr - 0.65) + 0.675 * (CN * (TCurr + 45) - 60)

    sum_melt *= step_time_delta.seconds / (3600 * (timedelta(hours=24) / step_time_delta))

    sum_snow = c_system.air_part.sum_snow
    sum = max(sum_melt, 0)

    result = min(sum, sum_snow)
    print("popov return %d (must be checked)" % result)

    return result
