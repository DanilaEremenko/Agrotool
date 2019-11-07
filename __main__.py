from agrotool_classes.OwningElement import OwningElement
from agrotool_classes.TAgroEcoSystem import TAgroEcoSystem, TAirPart, TWeatherRecord
from agrotool_classes.TRunController import TRunController
from agrotool_classes.TTechnologyDescriptor import TTechnologyDescriptor
from agrotool_classes.TWeatherController import TWeatherController

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


def ContinousRunning(hRunningController: TRunController):
    # Организация цикла по суточным шагам
    while OneStep(hRunningController):
        continue


def OneStep(hRunningController: TRunController):
    fcount = 0
    cDate = 0
    cWR, lastWR = 0, 0
    x, x0, Tave, sumSnow, delSnowPrec = 0, 0, 0, 0, 0
    bTime = None  #: real

    result = False

    print('Step1')
    # Один шаг модели за текущее число
    cWR = hRunningController.agroEcoSystem.Air_Part.currentEnv
    cDate = cWR.date
    Tave = cWR.Tave
    sumSnow = hRunningController.agroEcoSystem.Air_Part.sumSnow

    print('Step2')
    # Утренние технологические операции
    hRunningController.technologyDescriptor.Irrigation_Regime.stepoAct(hRunningController.agroEcoSystem)
    hRunningController.technologyDescriptor.Fertilization_Regime.stepoAct(hRunningController.agroEcoSystem)
    hRunningController.technologyDescriptor.Soil_Tillage_Regime.stepoAct(hRunningController.agroEcoSystem)

    print('Step3')
    # Семантические операции

    # Расчет баланса снега
    if (Tave < 0):
        sumSnow = sumSnow + cWR.Prec
        hRunningController.agroEcoSystem.Air_Part.alpha_snow = 0
    else:
        delSnowPrec = popov_melting(hRunningController.agroEcoSystem)  # Проверить формулу Попова
        cWR.Prec = cWR.Prec + delSnowPrec
        sumSnow = sumSnow - delSnowPrec

    print('Step6')
    # Радиация и фотосинтез(с потенциальным сопротивлением устьиц)
    RadPhotosynthesis(hRunningController.agroEcoSystem, False)

    print('Step7')
    # Водные потоки.Транспирация
    Evapotranspiration(hRunningController.agroEcoSystem)

    print('Step8')
    SoilTemperature(hRunningController.agroEcoSystem)

    print('Step9')
    # Расчет сумм осадков и транспирации
    x = hRunningController.agroEcoSystem.Air_Part.sumTrans
    x = x + hRunningController.agroEcoSystem.Crop_Part.Eplant + hRunningController.agroEcoSystem.Crop_Part.Esoil
    hRunningController.agroEcoSystem.Air_Part.sumTrans = x
    x0 = x
    x = hRunningController.agroEcoSystem.Air_Part.sumPrec
    x = x + cWR.Prec + cWR.Watering
    hRunningController.agroEcoSystem.Air_Part.sumPrec = x

    print('Step10')
    # Водные потоки в почве
    if (Tave >= 0):
        WaterSoilDynamics(hRunningController.agroEcoSystem)

    # Радиация и фотосинтез(с реальным сопротивлением устьиц)
    print('Step11')
    RadPhotosynthesis(hRunningController.agroEcoSystem, True)

    # Развитие
    print('Step12')
    RecalculateBioTime(hRunningController.agroEcoSystem)

    print('Step13')
    # Почвенно - азотный блок
    if (Tave >= 0) and (sumSnow < 1):
        RecalculateSoilNitrogen(hRunningController.agroEcoSystem)

    print('Step14')
    # Рост.Распределение ассимилятов
    if hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ifase > 1:
        Growth(hRunningController.agroEcoSystem)

    print('Step15')
    # Освежение динамических переменных
    hRunningController.agroEcoSystem.refreshing()
    hRunningController.agroEcoSystem.Air_Part.SumSnow = sumSnow

    print('Step16')
    # Добивание очередной строчки в файл выходных параметров
    TextOutput(hRunningController.agroEcoSystem, False)

    print('Step17')
    # Перевод даты на утро следующего дня
    cDate = cDate + 1

    # Очистка внешнего окружения
    lastWR = TWeatherRecord(hRunningController.agroEcoSystem.Air_Part.currentEnv.OwningElement, False)
    lastWR.Date = hRunningController.agroEcoSystem.Air_Part.currentEnv.date
    lastWR.Tmin = hRunningController.agroEcoSystem.Air_Part.currentEnv.Tmin
    lastWR.Tmax = hRunningController.agroEcoSystem.Air_Part.currentEnv.Tmax
    lastWR.Prec = hRunningController.agroEcoSystem.Air_Part.currentEnv.Prec
    lastWR.Tave = hRunningController.agroEcoSystem.Air_Part.currentEnv.Tave
    lastWR.Kex = hRunningController.agroEcoSystem.Air_Part.currentEnv.Kex
    lastWR.Watering = 0.0
    hRunningController.agroEcoSystem.Air_Part.currentEnv.Delete()
    # Получение нового состояния
    cWR = hRunningController.weatherController.GetMeteoData(0, cDate)

    if cWR is not None:
        # Увеличение какого - то счетчика
        fcount = fcount + 1
        if fcount > MAX_COUNT:  # (true) Этот счетчик больше критического
            result = True
            exit(0)

    else:
        lastWR.Date = cDate
        cWR = lastWR

    print('Step18')
    # Его присвоение
    hRunningController.agroEcoSystem.Air_Part.currentEnv = cWR
    bTime = hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ph_Time
    # RefreshVisualDate(cDate, bTime) # TODO
    result = hRunningController.technologyDescriptor.Harvesting_Regime.stepoAct(hRunningController.agroEcoSystem)

    print('Step19')
    TextOutput(hRunningController.agroEcoSystem, False)


if __name__ == '__main__':
    owningElement = OwningElement()
    currentEnv = TWeatherRecord(owningElement, False)
    airPart = TAirPart(currentEnv)
    agroEcoSystem = TAgroEcoSystem(airPart)
    technologyDescriptor = TTechnologyDescriptor()
    weatherControler = TWeatherController()
    hRunningController = TRunController(agroEcoSystem, technologyDescriptor, TWeatherController)

    ContinousRunning(hRunningController=hRunningController)
