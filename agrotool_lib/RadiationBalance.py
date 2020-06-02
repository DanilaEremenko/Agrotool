from agrotool_lib.PhysicalConstants import consSB
from numpy import exp


def get_albedo(LAI):
    """
    Вычисление альбедо почвы
    :param LAI:
    :return:
    """
    # TODO stub
    return 0


def get_NDVI(LAI, phTime):
    """
    Вычисление оптического индекса
    :param LAI:
    :param phTime:
    :return:
    """
    # TODO stub
    return 0


def get_fC(LAI):
    """
    Вычисление проективного покрытия
    :return:
    """
    # TODO stub
    return 0


def cons_correct_SB():
    # перевод из мегаджоулей/день в ватты
    return consSB * 10 ** 6 / (24 * 3600)


def calculate_balance(air_part, Rs, Kex, LAI, T_curr, delta_step, ph_time, mode='AllenFAO56'):
    """

    :param air_part:
    :param Rs:
    :param Kex:
    :param LAI:
    :param T_curr:
    :param delta_step:
    :param ph_time:
    :param mode:
    :return:
    """

    # расчитываем доходящую до поверхности почвы коротковолновную радиацию
    rad = Rs / delta_step.seconds
    rad = rad * Kex
    albedo = get_albedo(LAI)
    rad = (1 - albedo) * rad

    # расчет длинноволной радиации
    # TODO добавить учет относительной влажности
    Rnl = cons_correct_SB() * (T_curr + 273.15) ** 4 * (1.35 * Kex - 0.35)
    if Rnl < 0:
        print()

    # расчет радиационного баланса
    Rn = rad - Rnl

    # расчет потока тепла в почву
    if mode == 'AllenFAO56':
        if Rs > 0:  # day
            G = 0.1 * Rn
        else:
            G = 0.5 * Rn
    elif mode == 'METRIC1':
        G = Rn * T_curr * (0.0038 * 0.0074 * albedo) * (1 - 0.98 * get_NDVI(LAI, ph_time) ** 4)
    elif mode == 'METRIC2':
        if LAI >= 0.5:
            G = Rn * (0.05 * 0.18 * exp(-0.52 ** LAI))
        else:
            # TODO исправить
            G = Rn * (0.05 * 0.18 * exp(-0.52 ** LAI))
    elif mode == 'SEBS':
        G = Rn * (0.05 + 1 - get_fC(LAI)) * 0.265

    air_part.setBalanceParams(Rnl, Rn, G)
