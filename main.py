import json

from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem, TAirPart, TWeatherRecord
from agrotool_classes.TRunController import TRunController
from agrotool_classes.TTechnologyDescriptor import TTechnologyDescriptor
from agrotool_classes.TWeatherController import TWeatherController
from agrotool_classes.TDate import TDate

from agrotool_lib.Evap_base import Evapotranspiration, SoilTemperature
from agrotool_lib.RadPhot import RadPhotosynthesis
from agrotool_lib.WaterSoilDynamics import WaterSoilDynamics
from agrotool_lib.Development import RecalculateBioTime
from agrotool_lib.NitBal import RecalculateSoilNitrogen
from agrotool_lib.Growing import Growth
from agrotool_lib.OutputData import TextOutput
from agrotool_lib.Snowmelt import popov_melting

# const
MAX_COUNT = 4  # // Максимальное количество "битых" погодных записей


def pretty_print(text):
    divisor = "-------------------------"
    print("%s%s%s" % (divisor, text, divisor))


def RefreshVisualDate(cDate, bTime):
    # ModelForm.edDate.Text := DateToStr(cDate);
    # ModelForm.edDate.Refresh;
    # ModelForm.bioGauge.Position := trunc(bTime*100);
    # ModelForm.bioGauge.Refresh;
    # ModelForm.refreshSoilProfile;
    print("RefreshVisualDate empty")
    pass


def ContinousRunning(hRunningController: TRunController):
    # Организация цикла по суточным шагам
    for day in hRunningController.weatherMap.keys():
        print("____________\n____________\n DAY = %d\n____________\n____________\n" % day)
        OneStep(hRunningController)
        # TODO add step by fixed time delta and split dayily operation


def OneStep(hRunningController: TRunController):
    fcount = 0
    pretty_print('Step1')
    # Один шаг модели за текущее число
    cWR = hRunningController.get_curr_wr()
    cDate = cWR.date
    Tave = cWR.Tave
    sumSnow = hRunningController.agroEcoSystem.Air_Part.sumSnow

    # ------------------------------ day step -----------------------------------------------------------
    # if :
    pretty_print('Step2')
    # Утренние технологические операции
    hRunningController.technologyDescriptor.Irrigation_Regime.stepoAct(hRunningController.agroEcoSystem)
    hRunningController.technologyDescriptor.Fertilization_Regime.stepoAct(hRunningController.agroEcoSystem)
    hRunningController.technologyDescriptor.Soil_Tillage_Regime.stepoAct(hRunningController.agroEcoSystem)

    pretty_print('Step3')
    # Семантические операции

    # Расчет баланса снега
    if (Tave < 0):  # Если средняя температура < 0 - количество снега увеличивается
        sumSnow = sumSnow + cWR.Prec
        hRunningController.agroEcoSystem.Air_Part.alpha_snow = 0
    else:  # Иначе считаем таяние снега и прибавляем осадки
        delSnowPrec = popov_melting(hRunningController.agroEcoSystem)  # Проверить формулу Попова
        cWR.Prec = cWR.Prec + delSnowPrec
        sumSnow = sumSnow - delSnowPrec

    pretty_print('Step6')
    # Радиация и фотосинтез(с потенциальным сопротивлением устьиц)
    RadPhotosynthesis(hRunningController.agroEcoSystem, False)

    pretty_print('Step7')
    # Водные потоки.Транспирация
    Evapotranspiration(hRunningController.agroEcoSystem)

    pretty_print('Step8')
    SoilTemperature(hRunningController.agroEcoSystem)

    pretty_print('Step9')
    print("Some simple calculation without functions calls")
    # Расчет сумм осадков и транспирации
    hRunningController.agroEcoSystem.Air_Part.sumTrans = hRunningController.agroEcoSystem.Air_Part.sumTrans \
                                                         + hRunningController.agroEcoSystem.Crop_Part.Eplant \
                                                         + hRunningController.agroEcoSystem.Crop_Part.Esoil

    hRunningController.agroEcoSystem.Air_Part.sumPrec = hRunningController.agroEcoSystem.Air_Part.sumPrec \
                                                        + cWR.Prec \
                                                        + cWR.Watering

    pretty_print('Step10')
    # Водные потоки в почве
    if (Tave >= 0):
        WaterSoilDynamics(hRunningController.agroEcoSystem)
    else:
        print("RecalculateSoilNitrogen was't called (Tave = %d)" % (Tave))

    # Радиация и фотосинтез(с реальным сопротивлением устьиц)
    pretty_print('Step11')
    RadPhotosynthesis(hRunningController.agroEcoSystem, True)

    # Развитие
    pretty_print('Step12')
    RecalculateBioTime(hRunningController.agroEcoSystem)

    pretty_print('Step13')
    # Почвенно - азотный блок
    if (Tave >= 0) and (sumSnow < 1):
        RecalculateSoilNitrogen(hRunningController.agroEcoSystem)
    else:
        print("RecalculateSoilNitrogen was't called(Tave = %d, sumSnow = %d)" % (Tave, sumSnow))

    pretty_print('Step14')
    # Рост.Распределение ассимилятов
    if hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ifase > 1:
        Growth(hRunningController.agroEcoSystem)
    else:
        print("Growth was't called(Ifase = %d)" % (
            hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ifase))

    pretty_print('Step15')
    # Освежение динамических переменных
    hRunningController.agroEcoSystem.refreshing()
    hRunningController.agroEcoSystem.Air_Part.SumSnow = sumSnow

    pretty_print('Step16')
    # Добивание очередной строчки в файл выходных параметров
    TextOutput(hRunningController.agroEcoSystem, False)

    pretty_print('Step17')
    # Перевод даты на утро следующего дня
    cDate.inc_day()  # TODO шаг?

    # Очистка внешнего окружения
    lastWR = hRunningController.agroEcoSystem.Air_Part.currentEnv.__copy__()
    # Получение нового состояния
    hRunningController.inc_day()
    cWR = hRunningController.get_curr_wr()

    if cWR is not None:
        # Увеличение какого - то счетчика
        fcount = fcount + 1
        if fcount > MAX_COUNT:  # (true) Этот счетчик больше критического
            return True
    else:
        lastWR.Date = cDate
        cWR = lastWR

    pretty_print('Step18')
    # Его присвоение
    hRunningController.agroEcoSystem.Air_Part.currentEnv = cWR
    bTime = hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ph_Time
    RefreshVisualDate(cDate, bTime)
    result = hRunningController.technologyDescriptor.Harvesting_Regime.stepoAct(hRunningController.agroEcoSystem)

    pretty_print('Step19')
    TextOutput(hRunningController.agroEcoSystem, False)

    return result


if __name__ == '__main__':
    weatherMap = TWeatherRecord.get_map_from_json("environments/test_weather.json")
    airPart = TAirPart()
    agroEcoSystem = TAgroEcoSystem(airPart)
    technologyDescriptor = TTechnologyDescriptor()
    weatherControler = TWeatherController()
    hRunningController = TRunController(agroEcoSystem, technologyDescriptor, weatherControler, weatherMap)

    ContinousRunning(hRunningController=hRunningController)
