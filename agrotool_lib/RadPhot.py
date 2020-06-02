# TODO check functions
from agrotool_lib.RadiationAstronomy import get_day_length
from .RadiationAstronomy import *
from numpy import exp, sqrt, sin, cos, pi
from .PhysicalConstants import RConst1, RConst2, RConst3


def rad_photosynthesis(c_system, isBio):
    # Расчет коэффициента поглощения ФАР на глубине
    def AP(cLAI):
        a = -RConst1 * cLAI / shour
        if a < -9.0:
            a = -9.0
        al = RConst2 * (exp(a * RConst3) - exp(a))
        result = (dir_diff * exp(a) + exp(-cLAI)) / (dir_diff + 1) + al

        return result

    def LAI_splitting():
        pulLAI = 0.5
        ssLAI = sumLAI
        rLAI = 0
        while (True):
            if (ssLAI < pulLAI):
                rLAI = rLAI + ssLAI
                lai_levels.append(rLAI)
                ssLAI = -1

            else:
                rLAI = rLAI + pulLAI
                lai_levels.append(rLAI)
                ssLAI = ssLAI - pulLAI
                pulLAI = pulLAI * 1.5

            if (ssLAI <= 0):
                break

        pass

    # Расчет температурной функции стресса на максимальную интенсивность фотосинтеза
    def FStr(x):
        result = 0
        if Tave < 0:
            pass

        if x <= 12.0:
            result = exp((-sqrt(x - 12) / 49))
        elif x >= 25.0:
            result = exp((-sqrt(x - 25) / 49))

        return result

    # Расчет мгновенной интенсивности фотсинтеза единичной поверхности листа
    def photosynthesis(cRad):
        uRad = cRad / 3600
        a = ResSum
        JFAR = (alfa * uRad * PhMax) / (PhMax + alfa * uRad)
        b = ConcCo21 + (ResSum + Rx) * JFAR
        c = ConcCo21 * JFAR
        d = b * b - 4 * a * c
        x = (b - sqrt(d)) / (2 * a)  # TODO D == d?
        Result = (x - Dresp) * 3600
        if Result < 0:
            Result = 0

        return Result

    def increas_CO2(co2, isNow):
        dn = EncodeDate(1961, 1, 1)  # TODO EncodeDate
        df = EncodeDate(2080, 1, 1)  # TODO EncodeDate
        dp = EncodeDate(2010, 1, 1)  # TODO EncodeDate
        dc = c_system.Air_Part.currentEnv.Date
        if (dc < dp):
            result = co2 + (73 / 317.5) * co2 * (dc - dn) / (dp - dn)
        else:
            if (isNow):
                result = co2 + (450.1 / 317.5) * co2 * (dc - dn) / (df - dn)
            else:
                result = (390.5 / 317.5) * co2

        return result

    # ---------------------------- RadPhotosynthesis main --------------------------------------------
    lai_levels = []
    # Рассчитывает следующие переменные
    # 1. Коротковолновые составлящие суточного радиационного баланса для почвы и верхней кромки посева
    # 2. Суточный фотосинтез посева (прирост углеродных ассимилятов)
    # Берем широту
    Iday = c_system.RunController.get_current_day().date.date.days
    fi = c_system.RunController.measurementUnit.Latitude
    dl = get_day_length(fi, Iday)
    # Переводим широту в радианы
    FiRad = fi * pi / 180
    # Берем коэффициент ослабления радиации
    Kex = c_system.Air_Part.currentEnv.Kex
    # Вычисляем номер дня

    # Годовой угол
    sd = 0.4102 * sin(0.0172 * (Iday - 80.25))
    # Константы суточного хода Солнца
    b1 = sin(FiRad) * sin(sd)
    b2 = cos(FiRad) * cos(sd)
    slope_psi = c_system.RunController.measurementUnit.SlopeAzimuth * pi / 180
    slope_al = c_system.RunController.measurementUnit.SlopeSteepness * pi / 180
    hour1 = 12 - dl / 2
    total_flux_rad = 0.0

    sumLAI = c_system.Crop_Part.Individual_Plant.Shoot.Leaf.AreaIndex
    sumSAI = c_system.Crop_Part.Individual_Plant.Shoot.Stem.AreaIndex

    LAI_splitting()

    # Вычисляем суммарное сопротивление, функцию стресса и новый PhMax
    ResStom = c_system.Crop_Part.Individual_Plant.Shoot.Leaf.ResStom

    # Берем среднюю температуру
    Tave = c_system.Air_Part.currentEnv.Tave

    ResSum = 1.6 * ResStom + c_system.Crop_Part.Individual_Plant.Culture_Descriptor.Photosynthesis_Type_Descriptor.ResMes
    PhMax = c_system.Crop_Part.Individual_Plant.Culture_Descriptor.Photosynthesis_Type_Descriptor.PHMax
    PhMax = PhMax * FStr(Tave)
    Dresp = PhMax * c_system.Crop_Part.Individual_Plant.Culture_Descriptor.Photosynthesis_Type_Descriptor.CExpen

    co2 = c_system.RunController.measurementUnit.CO2Conc

    # Брнофигня
    # co2 = increas_CO2(co2, false)
    ConcCo21 = co2 + ResSum * Dresp

    alfa = c_system.Crop_Part.Individual_Plant.Culture_Descriptor.Photosynthesis_Type_Descriptor.alpha
    Rx = c_system.Crop_Part.Individual_Plant.Culture_Descriptor.Photosynthesis_Type_Descriptor.Rx
    prim_ass = 0
    rsh_plant = 0
    rsh_soil = 0

    while (True):
        hour2 = hour1 + 1
        if (hour2 > 12 + dl / 2):
            hour2 = 12 + dl / 2
        shour1 = sinhour(hour1, b1, b2)
        shour2 = sinhour(hour2, b1, b2)
        shour = sinhour((hour1 + hour2) / 2, b1, b2)

        # Коротковолнвая радиция
        # Без учета склона
        # c_flux_rad = 0.5*(AQR(shour1) + AQR(shour2))*(hour2-hour1)
        # С учетом склона
        c_flux_rad = 0.5 * (aqr_slope(hour1, FiRad, sd, slope_psi, slope_al)
                            + aqr_slope(hour2, FiRad, sd, slope_psi, slope_al)) * (hour2 - hour1)

        if (shour < 0.01):
            shour = 0.01

        # Ослабляем радиацю
        c_flux_rad = c_flux_rad * Kex

        # А было так
        if Kex > 0.95:
            Srel = 0.1 / shour
            if Srel > 1: Srel = 1
            c_diff_rad = c_flux_rad * Srel
            cDirectRad = c_flux_rad - c_diff_rad
        else:
            c_diff_rad = c_flux_rad
            cDirectRad = 0

        if (c_diff_rad < 0.0000001):
            dir_diff = 0
        else:
            dir_diff = cDirectRad / c_diff_rad

        # Считаем ak
        ak = shour / (2.09 * shour + 0.22)
        # arp_P = 0.07 * (exp(-1.252 * shour)) TODO unused
        arp_S = 0.23

        # Считаем ФАР
        c_phar_rad = c_flux_rad * (dir_diff * ak + 0.6) / (1.0 + dir_diff)
        Rpb1 = c_flux_rad * (1 - arp_S)

        # TODO Еще всякого вычисляем...
        copr = 1.0 - exp(-2 * sumLAI)
        rsh_plant = rsh_plant + c_flux_rad * (1 - arp_S) * (1 - AP(sumLAI)) * copr
        rsh_soil = rsh_soil + c_flux_rad * ((1 - copr) + copr * AP(sumLAI)) * (1 - arp_S)

        total_flux_rad = total_flux_rad + c_flux_rad
        # Теперь накапливаем то, что нужно для фотосинтеза
        brphot = 0
        x1 = AP(0.0)

        if (isBio):

            for i in range(0, len(lai_levels)):
                # ФАР, дошедшая до нижней границы слоя
                x2 = AP(lai_levels[i])
                # Доля поглощенной ФАР
                x3 = x1 - x2
                # Поглощенная ФАР
                rph = c_phar_rad * x3
                # Перекид для будущего
                x1 = x2
                if (lai_levels[i] > 0):
                    # Считаем долю LAI в слое
                    if i == 0:
                        xs = lai_levels[i] / sumLAI
                    else:
                        xs = (lai_levels[i] - lai_levels[i - 1]) / sumLAI
                    # Считаем суммарный листостеблевой индекс в текущем слое
                    if i == 0:
                        xL = lai_levels[i] + xs * sumSAI
                    else:
                        xL = (lai_levels[i] - lai_levels[i - 1]) + xs * sumSAI
                    # Считаем ФАР на единицу поверхности ЛИСТА
                    phpli = rph / xL
                    if Tave > 0:
                        # Накопление первичных ассимилятов
                        PhotLAI = photosynthesis(phpli)
                        brphot = brphot + PhotLAI * xL

        prim_ass = prim_ass + brphot

        hour1 = hour2
        if (hour2 >= 12 + dl / 2 - 0.000001):
            break

        c_system.Crop_Part.Individual_Plant.PrimAss = prim_ass

        # Запоминаем приходящщу радиацию
        c_system.Air_Part.SumRad = total_flux_rad
        # Запоминаем перехваченну радиацию
        c_system.Crop_Part.RshPlant = rsh_plant
        # Запоминаем почвенну радиацию
        c_system.Soil_Part.SoilSurface.RshSoil = rsh_soil
        # Запоминаим каэфициент праиктивнава пакрытия
        c_system.Crop_Part.copr = copr
