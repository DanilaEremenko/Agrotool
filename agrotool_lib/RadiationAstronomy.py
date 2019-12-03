from numpy import sin, cos, pi, arctan, sqrt, arccos
from .PhysicalConstants import SolarConst
from agrotool_classes.TDate import TDate


def sinhour(hour, b1, b2):
    # Рассчитывает угол склонения Солнца
    # Вычисление часового угла
    tau = cos((hour - 12) * pi / 12)
    # Синус склонения Солнца
    return b1 + b2 * tau


def AQR(shour):
    # Рассчитывает часовой поток приходящей к верхней границе атмосферы КВР
    # Часовой поток
    return SolarConst / 60 * shour


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


def GetCurrRad(fi, cDate: TDate):
    # Переводим широту в радианы
    FiRad = fi * pi / 180
    # Вычисляем номер дня
    Iday = cDate.get_day()  # TODO day of the year
    # Годовой угол
    sd = 0.4102 * sin(0.0172 * (Iday - 80.25))

    b1 = sin(FiRad) * sin(sd)
    b2 = cos(FiRad) * cos(sd)

    shour1 = sinhour(cDate.get_hour(), b1, b2)
    return AQR(shour1) if shour1 > 0 else 0


def GetCurrSumRad(fi, cDate, delta: TDate):
    if delta.date.seconds < TDate(hours=1).date.seconds:
        return GetCurrRad(fi, cDate) * delta.get_seconds()
    else:
        step_num = int(delta.get_hour() + 1)
        delta_step = TDate(delta.date.seconds / step_num)

        currDate = cDate + TDate(seconds=delta_step.date.seconds / 2)
        sumRad = 0
        for i in range(0, step_num):
            sumRad += GetCurrRad(fi, currDate) * delta_step.get_seconds()
            currDate += delta_step
        return sumRad
