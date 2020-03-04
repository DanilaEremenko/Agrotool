import numpy as np

from core import MatplotlibVisualizing
from core import PlotlyVisualizing

from agrotool_classes.TAgroEcoSystem import TWeatherRecord
from agrotool_classes.TRunController import TRunController

from agrotool_lib.EvapBase import Evapotranspiration, SoilTemperature
from agrotool_lib import Precipitation
from agrotool_lib.RadiationAstronomy import GetCurrSumRad, _DayLength
from agrotool_lib.WaterSoilDynamics import WaterSoilDynamics
from agrotool_lib.Development import RecalculateBioTime
from agrotool_lib.NitBal import RecalculateSoilNitrogen
from agrotool_lib.Growing import Growth
from agrotool_lib.Snowmelt import popov_melting

from datetime import datetime, timedelta
import pandas as pd

# const
MAX_COUNT = 4  # // Максимальное количество "битых" погодных записей


def pretty_print(text):
    divisor = "-------------------------"
    print("%s%s%s" % (divisor, text, divisor))


def OneDayStep(hRunningController: TRunController,
               cWR: TWeatherRecord,
               nextWR: TWeatherRecord,
               stepTimeDelta: timedelta,
               historyDict):
    print("____________\n____________\n DAY = %s\n____________\n____________\n" % cWR.date.__str__())
    Tave = cWR.Tave
    sumSnow = hRunningController.agroEcoSystem.airPart.SumSnow
    timeForDailyOperation = timedelta(hours=12)

    # hours calulation
    noonTime = datetime(year=cWR.date.year,  # for calculation from sunrise to sunrise of next day
                        month=cWR.date.month,
                        day=cWR.date.day,
                        hour=14)
    fi = hRunningController.region.Latitude
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

    ##############################################################################
    # ------------------------------ day step (Delta loop) -----------------------
    ##############################################################################
    for cDateTime, T_curr, Prec_curr in zip(timeHistory, T_history, prec_history):

        ##########################################################################
        # ------------------------- Ежедневные операции --------------------------
        ##########################################################################
        pretty_print('Step2')
        if cDateTime.second / 60 == timeForDailyOperation.seconds / 60:
            # Утренние технологические операции
            hRunningController.technologyDescriptor.Irrigation_Regime.stepoAct(hRunningController.agroEcoSystem)
            hRunningController.technologyDescriptor.Fertilization_Regime.stepoAct(hRunningController.agroEcoSystem)
            hRunningController.technologyDescriptor.Soil_Tillage_Regime.stepoAct(hRunningController.agroEcoSystem)
        else:
            print("Not now")

        ##########################################################################
        # ------------------------- Расчет баланса снега -------------------------
        ##########################################################################
        # Семантические операции
        pretty_print('Step3')
        if (T_curr < 0):  # Если текущая температура < 0 - количество снега увеличивается
            sumSnow = sumSnow + Prec_curr
            hRunningController.agroEcoSystem.airPart.alpha_snow = 0
        else:  # Иначе считаем таяние снега и прибавляем осадки
            delSnowPrec = popov_melting(hRunningController.agroEcoSystem, cDateTime, stepTimeDelta,
                                        T_curr)  # Проверить формулу Попова
            print(cDateTime)
            Prec_curr += delSnowPrec
            sumSnow = sumSnow - delSnowPrec

        ##########################################################################
        # ---- Радиация и фотосинтез(с потенциальным сопротивлением устьиц) ------
        ##########################################################################
        pretty_print('Step6')
        # Запоминаем приходящщу радиацию
        # Запоминаем почвенну радиацию
        # RadPhotosynthesis(hRunningController.agroEcoSystem, False)#TODO
        hRunningController.agroEcoSystem.airPart.SumRad = GetCurrSumRad(fi, cDateTime, stepTimeDelta)

        ##########################################################################
        # --------------------- Водные потоки.Транспирация -----------------------
        ##########################################################################
        pretty_print('Step7')
        Evapotranspiration(hRunningController.agroEcoSystem)

        pretty_print('Step8')
        SoilTemperature(
            cSystem=hRunningController.agroEcoSystem,
            T_curr=T_curr
        )

        ##########################################################################
        # ---------------------Расчет сумм осадков и транспирации ---------------- # TODO next step
        ##########################################################################
        pretty_print('Step9')
        print("Some simple calculation without functions calls")

        hRunningController.agroEcoSystem.airPart.sumTrans = hRunningController.agroEcoSystem.airPart.sumTrans \
                                                            + hRunningController.agroEcoSystem.cropPart.Eplant \
                                                            + hRunningController.agroEcoSystem.cropPart.Esoil

        hRunningController.agroEcoSystem.airPart.sumPrec = hRunningController.agroEcoSystem.airPart.sumPrec \
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
        if hRunningController.agroEcoSystem.cropPart.Individual_Plant.Ifase > 1:
            Growth(hRunningController.agroEcoSystem)
        else:
            print("Growth was't called(Ifase = %d)" % (
                hRunningController.agroEcoSystem.cropPart.Individual_Plant.Ifase))

        pretty_print('Step15')
        # Освежение динамических переменных
        hRunningController.agroEcoSystem.refreshing()
        hRunningController.agroEcoSystem.airPart.SumSnow = sumSnow

        pretty_print('Step17')

        pretty_print('Step18')
        # Его присвоение
        hRunningController.agroEcoSystem.airPart.currentEnv = cWR
        bTime = hRunningController.agroEcoSystem.cropPart.Individual_Plant.Ph_Time

        ##########################################################################
        # ------------------------------ weather history -------------------------
        ##########################################################################
        historyDict['weather'] = historyDict['weather'].append(
            pd.DataFrame(
                {
                    "Date": [cDateTime],
                    "T": [T_curr],
                    "Rad": [
                        hRunningController.agroEcoSystem.airPart.SumRad * 10_000 / stepTimeDelta.seconds],
                    "Prec": [Prec_curr],
                    "SumSnow": [sumSnow]
                }
            )
        )
        ##########################################################################
        # ------------------------------ soil history ----------------------------
        ##########################################################################
        t = []
        T = np.zeros(len(hRunningController.agroEcoSystem.soilPart.soilLayers))
        layers = list(range(len(T)))
        for i, layer in enumerate(hRunningController.agroEcoSystem.soilPart.soilLayers):
            t.append(cDateTime)
            T[i] = layer.T

        historyDict['soil'] = historyDict['soil'].append(
            pd.DataFrame(
                {
                    't': t,
                    'layer': layers,
                    'layer_sym': list(map(lambda layer: "layer_%d" % layer, layers)),
                    'T': T
                }
            )
        )

        # Временной шаг
        cDateTime += stepTimeDelta


def ContinousRunning(hRunningController: TRunController):
    # Организация цикла по суточным шагам

    historyDict = {
        'weather': pd.DataFrame(
            {
                "Date": np.empty(0),
                "T": np.empty(0),
                "Rad": np.empty(0),
                "Prec": np.empty(0),
                "SumSnow": np.empty(0),
            }
        ),
        'soil': pd.DataFrame(
            {
                't': np.empty(0),
                'layer': np.empty(0),
                'layer_sym': np.empty(0),
                'T': np.empty(0)
            }
        )
    }
    weatherIter = iter(hRunningController.weatherDf.to_dict(orient='records'))
    weatherIter.__next__()
    for cWR in hRunningController.weatherDf.to_dict(orient='records'):

        cWR = TWeatherRecord(cWR)

        try:  # nextWR necessary in OneDayStep
            nextWR = TWeatherRecord(weatherIter.__next__())
        except StopIteration:  # for last day
            nextWR = cWR.__copy__()
            nextWR.date += timedelta(days=1)

        OneDayStep(
            hRunningController,
            cWR=cWR, nextWR=nextWR,
            stepTimeDelta=timedelta(hours=1 / 2),
            historyDict=historyDict
        )

    historyDict['weather'].set_index("Date", inplace=True)

    print("plotting simple histories")

    MatplotlibVisualizing.show_from_df(df=historyDict['weather'])
    PlotlyVisualizing.show_from_df(df=historyDict['weather'])

    print("plotting temperature history in soil (it will be longer than previous plotting)")

    # show soil_layers.T for 10 days on dynamic graphic
    show_day_num = int(len(historyDict['soil']) * 10 / len(hRunningController.weatherDf))
    historyDict['soil']['t'] = pd.to_numeric(historyDict['soil']['t'])
    PlotlyVisualizing.show_soil_from_df(
        df=historyDict['soil']
            .head(show_day_num)
            .sort_values(by=['layer', 't'])
    )


def main():
    hRunningController = TRunController(
        weatherPath="environments/test_1/weather1.json",
        modelPath="environments/test_1/model_params.json",
        placePath="environments/test_1/place.json"

    )

    hRunningController.update_params('environments/test_1/query_solidgrids.json')
    hRunningController.init_start(jsonPath='environments/test_1/initial_state.json')

    ContinousRunning(hRunningController=hRunningController)


if __name__ == '__main__':
    main()
