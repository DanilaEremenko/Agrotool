from numpy import sin, cos, pi, arctan, sqrt, arccos
from .PhysicalConstants import SolarConst


def sinhour(hour, b1, b2):
    # Рассчитывает угол склонения Солнца
    # Вычисление часового угла
    tau = cos((hour - 12) * pi / 12)
    # Синус склонения Солнца
    return b1 + b2 * tau


def AQR(shour):
    # Рассчитывает часовой поток приходящей к верхней границе атмосферы КВР
    # Часовой поток
    return SolarConst / 4.187 * 60 * shour


def AQR_SLOPE(hour, fir, sd, psin, al):
    # { Назначение: pасчет потока пpиходящей к склону КВР без учета ослабления
    # SinH  - синус высоты стояния солнца sinus of sun height
    # Cosi - косинус угла между склоном и солнцем}
    b1 = sin(fir) * sin(sd)
    b2 = cos(fir) * cos(sd)

    # {Часовой угол}
    tau = (hour - 12) * pi / 12

    # {Высота солнца над горизонтом}
    sinh = b1 + b2 * cos(tau)
    cosh = sqrt(1 - sqrt(sinh))

    # {ВЫЧИСЛЕНИЕ АЗИМУТА СОЛНЦА}
    tgp = sin(tau) * cos(sd) / (sin(fir) * cos(sd) * cos(tau) - cos(fir) * sin(sd) + 1e-9)
    if (tgp > 600):
        psi = pi / 2
    else:
        if (tgp < -600):
            psi = -pi / 2
        else:
            psi = arctan(tgp)
    if ((sin(fir) * cos(sd) * cos(tau) - cos(fir) * sin(sd)) > 0):
        psi = psi + pi

    # {Азимутальный угол между склоном и Солнцем}
    psip = psi - psin

    # {Угол падения лучей на склон}
    cosi = cos(al) * sinh + sin(al) * cosh * cos(psip)

    if cosi < 0: cosi = 0

    return (SolarConst / 4.187) * 60 * cosi


def _DayLength(fi, cDate):
    # Calculate value into Result and place the required subscriptions
    # Вычисляет длину дня по широте и дате
    # Переводим широту в радианы
    FiRad = fi * pi / 180
    # Вычисляем номер дня
    Iday = cDate  # TODO day of the year
    # Годовой угол
    sd = 0.4102 * sin(0.0172 * (Iday - 80.25))
    # Момент восхода
    ch = -(sin(FiRad) * sin(sd) / (cos(FiRad) * cos(sd)))
    aSunRise = arccos(ch)
    return 24 * aSunRise / pi


def _SumRad(fi, cDate):
    dl = _DayLength(fi, cDate)
    # Переводим широту в радианы
    FiRad = fi * pi / 180
    # Вычисляем номер дня
    Iday = cDate  # TODO day of the year
    # Годовой угол
    sd = 0.4102 * sin(0.0172 * (Iday - 80.25))
    # Константы суточного хода Солнца
    b1 = sin(FiRad) * sin(sd)
    b2 = cos(FiRad) * cos(sd)
    hour1 = 12 - dl / 2
    TotalFluxRad = 0.0
    while (True):
        hour2 = hour1 + 1
        if (hour2 > 12 + dl / 2):
            hour2 = 12 + dl / 2
        shour1 = sinhour(hour1, b1, b2)
        shour2 = sinhour(hour2, b1, b2)
        cFluxRad = 0.5 * (AQR(shour1) + AQR(shour2)) * (hour2 - hour1)
        TotalFluxRad = TotalFluxRad + cFluxRad
        hour1 = hour2
        if (hour2 >= 12 + dl / 2):
            break

    return TotalFluxRad
