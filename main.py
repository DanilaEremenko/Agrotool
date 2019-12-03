from agrotool_classes.TAgroEcoSystem import TWeatherRecord
from agrotool_classes.TRunController import TRunController

from agrotool_classes.TWeatherHistory import TWeatherHistory, DayWeather

from agrotool_lib.Evap_base import Evapotranspiration, SoilTemperature
from agrotool_lib.RadPhot import RadPhotosynthesis
from agrotool_lib.RadiationAstronomy import GetCurrSumRad
from agrotool_lib.WaterSoilDynamics import WaterSoilDynamics
from agrotool_lib.Development import RecalculateBioTime
from agrotool_lib.NitBal import RecalculateSoilNitrogen
from agrotool_lib.Growing import Growth
from agrotool_lib.OutputData import TextOutput
from agrotool_lib.Snowmelt import popov_melting

from datetime import datetime, timedelta

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
    weatherHistory = TWeatherHistory()
    for cWR in hRunningController.weatherList:
        weatherHistory.append_day(cWR, OneDayStep(hRunningController, cWR, timeDelta=timedelta(hours=1)))
    weatherHistory.show_all_days()


def OneDayStep(hRunningController: TRunController, cWR: TWeatherRecord, timeDelta: timedelta):
    print("____________\n____________\n DAY = %s\n____________\n____________\n" % cWR.date.__str__())
    dayWeatherHistory = DayWeather()
    pretty_print('Step1')
    # Один шаг модели за текущее число
    cDate = cWR.date
    Tave = cWR.Tave
    sumSnow = hRunningController.agroEcoSystem.Air_Part.sumSnow
    timeForDailyOperation = timedelta(hours=12)
    stepNum = timedelta(days=1) / timeDelta
    timeStep = 24 / stepNum
    Tcurr = cWR.Tmin
    Tstep = (cWR.Tmax - cWR.Tmin) / stepNum
    fi = hRunningController.measurementUnit.Latitude
    # ------------------------------ day step -----------------------------------------------------------
    # Delta loop
    i = 0
    while cDate.day == cWR.date.day:

        # Daily operation check
        pretty_print('Step2')
        if cDate.second / 60 == timeForDailyOperation.seconds / 60:
            # Утренние технологические операции
            hRunningController.technologyDescriptor.Irrigation_Regime.stepoAct(hRunningController.agroEcoSystem)
            hRunningController.technologyDescriptor.Fertilization_Regime.stepoAct(hRunningController.agroEcoSystem)
            hRunningController.technologyDescriptor.Soil_Tillage_Regime.stepoAct(hRunningController.agroEcoSystem)
        else:
            print("Not now")

        # TODO here we go using delta
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
        # Запоминаем приходящщу радиацию
        print("BEFORE:Air.SumRad = %d" % hRunningController.agroEcoSystem.Air_Part.SumRad)
        print("BEFORE:Crop.RshPlant = %d" % hRunningController.agroEcoSystem.Crop_Part.RshPlant)
        print("BEFORE:Crop.corp = %d" % hRunningController.agroEcoSystem.Crop_Part.copr)
        # Запоминаем почвенну радиацию
        # RadPhotosynthesis(hRunningController.agroEcoSystem, False)#TODO
        hRunningController.agroEcoSystem.Air_Part.SumRad = GetCurrSumRad(fi, cDate, timeDelta)
        print("AFTER:Air.SumRad = %d" % hRunningController.agroEcoSystem.Air_Part.SumRad)
        print("AFTER:Crop.RshPlant = %d" % hRunningController.agroEcoSystem.Crop_Part.RshPlant)
        print("AFTER:Crop.corp = %d" % hRunningController.agroEcoSystem.Crop_Part.copr)

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
        # RadPhotosynthesis(hRunningController.agroEcoSystem, True)

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
        # Временной шаг
        cDate += timeDelta

        pretty_print('Step18')
        # Его присвоение
        hRunningController.agroEcoSystem.Air_Part.currentEnv = cWR
        bTime = hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ph_Time
        RefreshVisualDate(cDate, bTime)

        pretty_print('Step19')
        TextOutput(hRunningController.agroEcoSystem, False)

        dayWeatherHistory.append(
            Rad=hRunningController.agroEcoSystem.Air_Part.SumRad * 10_000 / timeDelta.seconds,
            T=Tcurr,
            delta=i)
        i += timeStep
        Tcurr += Tstep

    return dayWeatherHistory


if __name__ == '__main__':
    weatherList = TWeatherRecord.get_list_from_json("environments/test_1/weather.json")
    hRunningController = TRunController(weatherList=weatherList)

    ContinousRunning(hRunningController=hRunningController)
