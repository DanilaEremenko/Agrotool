import numpy as np

from core.DataProcessor import get_df_from_json
from core import MatplotlibVisualizing
from core import PlotlyVisualizing

from agrotool_classes.TAgroEcoSystem import TWeatherRecord
from agrotool_classes.TRunController import TRunController
from agrotool_classes.TWeatherHistory import TWeatherHistory

from agrotool_lib.Evap_base import Evapotranspiration, SoilTemperature
from agrotool_lib import Precipitation
from agrotool_lib.RadiationAstronomy import GetCurrSumRad, _DayLength
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


def OneDayStep(hRunningController: TRunController,
               cWR: TWeatherRecord,
               nextWR: TWeatherRecord,
               stepTimeDelta: timedelta,
               weatherHistory: TWeatherHistory):
    print("____________\n____________\n DAY = %s\n____________\n____________\n" % cWR.date.__str__())
    pretty_print('Step1')
    # Один шаг модели за текущее число
    Tave = cWR.Tave
    sumSnow = hRunningController.agroEcoSystem.Air_Part.SumSnow
    timeForDailyOperation = timedelta(hours=12)

    # hours calulation
    noonTime = datetime(year=cWR.date.year,  # for calculation from sunrise to sunrise of next day
                        month=cWR.date.month,
                        day=cWR.date.day,
                        hour=14)
    fi = hRunningController.measurementUnit.Latitude
    currDayLength = timedelta(hours=_DayLength(fi, cWR.date))
    nextDayLength = timedelta(hours=_DayLength(fi, nextWR.date))
    currSunriseDate = noonTime - currDayLength / 2
    nextSunriseDate = noonTime - nextDayLength / 2 + timedelta(days=1)

    # temperature calculation
    T_history = np.array(
        [*np.linspace(cWR.Tmin, cWR.Tmax, num=int((noonTime - currSunriseDate) / stepTimeDelta))[0:-1],
         *np.linspace(cWR.Tmax, nextWR.Tmin, num=int((nextSunriseDate - noonTime) / stepTimeDelta) + 2)]
    )
    timeHistory = [currSunriseDate + stepTimeDelta * i for i in range(0, len(T_history))]

    prec_history = Precipitation.get_precipitation_history(cWR.Prec, T_history)

    # ------------------------------ day step -----------------------------------------------------------
    # Delta loop
    for cDateTime, T_curr, Prec_curr in zip(timeHistory, T_history, prec_history):

        # Daily operation check
        pretty_print('Step2')
        if cDateTime.second / 60 == timeForDailyOperation.seconds / 60:
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
        if (T_curr < 0):  # Если текущая температура < 0 - количество снега увеличивается
            sumSnow = sumSnow + Prec_curr
            hRunningController.agroEcoSystem.Air_Part.alpha_snow = 0
        else:  # Иначе считаем таяние снега и прибавляем осадки
            delSnowPrec = popov_melting(hRunningController.agroEcoSystem, cDateTime, stepTimeDelta,
                                        T_curr)  # Проверить формулу Попова
            print(cDateTime)
            Prec_curr += delSnowPrec
            sumSnow = sumSnow - delSnowPrec

        pretty_print('Step6')
        # Радиация и фотосинтез(с потенциальным сопротивлением устьиц)
        # Запоминаем приходящщу радиацию
        print("BEFORE:Air.SumRad = %d" % hRunningController.agroEcoSystem.Air_Part.SumRad)
        print("BEFORE:Crop.RshPlant = %d" % hRunningController.agroEcoSystem.Crop_Part.RshPlant)
        print("BEFORE:Crop.corp = %d" % hRunningController.agroEcoSystem.Crop_Part.copr)
        # Запоминаем почвенну радиацию
        # RadPhotosynthesis(hRunningController.agroEcoSystem, False)#TODO
        hRunningController.agroEcoSystem.Air_Part.SumRad = GetCurrSumRad(fi, cDateTime, stepTimeDelta)
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

        pretty_print('Step18')
        # Его присвоение
        hRunningController.agroEcoSystem.Air_Part.currentEnv = cWR
        bTime = hRunningController.agroEcoSystem.Crop_Part.Individual_Plant.Ph_Time

        pretty_print('Step19')
        TextOutput(hRunningController.agroEcoSystem, False)

        weatherHistory.append_frame(
            {
                "Date": [cDateTime],
                "T": [T_curr],
                "Rad": [
                    hRunningController.agroEcoSystem.Air_Part.SumRad * 10_000 / stepTimeDelta.seconds],
                "Prec": [Prec_curr],
                "SumSnow": [sumSnow]
            }
        )

        # Временной шаг
        cDateTime += stepTimeDelta


def ContinousRunning(hRunningController: TRunController):
    # Организация цикла по суточным шагам
    weatherHistory = TWeatherHistory()
    weatherIter = iter(hRunningController.weatherDf.to_dict(orient='records'))
    weatherIter.__next__()
    for cWR in hRunningController.weatherDf.to_dict(orient='records'):

        cWR = TWeatherRecord(cWR)

        try:  # nextWR necessary in OneDayStep
            nextWR = TWeatherRecord(weatherIter.__next__())
        except StopIteration:  # for last day
            nextWR = cWR.__copy__()
            nextWR.date += timedelta(days=1)

        OneDayStep(hRunningController,
                   cWR=cWR, nextWR=nextWR,
                   stepTimeDelta=timedelta(hours=1 / 2),
                   weatherHistory=weatherHistory)

    weatherHistory.df = weatherHistory.df.set_index("Date")

    MatplotlibVisualizing.show_from_df(df=weatherHistory.df)

    PlotlyVisualizing.show_from_df(df=weatherHistory.df)


def main():
    hRunningController = TRunController(weatherDf=get_df_from_json("environments/test_1/weather.json"))
    ContinousRunning(hRunningController=hRunningController)


if __name__ == '__main__':
    main()
