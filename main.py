import numpy as np

from agrotool_lib.RadiationBalance import calculate_balance
from core import MatplotlibVisualizing
from core import PlotlyVisualizing

from agrotool_classes.TAgroEcoSystem import TWeatherRecord
from agrotool_classes.TRunController import TRunController

from agrotool_lib.EvapBase import evapo_transpiration, soil_temperature
from agrotool_lib import Precipitation
from agrotool_lib.RadiationAstronomy import get_curr_sum_rad, get_day_length
from agrotool_lib.WaterSoilDynamics import water_soil_dynamics
from agrotool_lib.Development import recalculate_bio_time
from agrotool_lib.NitBal import recalculate_soil_nitrogen
from agrotool_lib.Growing import growth
from agrotool_lib.Snowmelt import popov_melting

from datetime import datetime, timedelta
import pandas as pd

# const
MAX_COUNT = 4  # // Максимальное количество "битых" погодных записей


def pretty_print(text):
    divisor = "-------------------------"
    print("%s%s%s" % (divisor, text, divisor))


def OneDayStep(h_running_controller: TRunController,
               cWR: TWeatherRecord,
               nextWR: TWeatherRecord,
               stepTimeDelta: timedelta,
               historyDict):
    print("____________\n____________\n DAY = %s\n____________\n____________\n" % cWR.date.__str__())
    Tave = cWR.temp_avg
    sum_snow = h_running_controller.agro_eco_system.air_part.sum_snow
    timeForDailyOperation = timedelta(hours=12)

    # hours calulation
    noonTime = datetime(year=cWR.date.year,  # for calculation from sunrise to sunrise of next day
                        month=cWR.date.month,
                        day=cWR.date.day,
                        hour=14)
    fi = h_running_controller.region.Latitude
    currDayLength = timedelta(hours=get_day_length(fi, cWR.date))
    nextDayLength = timedelta(hours=get_day_length(fi, nextWR.date))
    currSunriseDate = noonTime - currDayLength / 2
    nextSunriseDate = noonTime - nextDayLength / 2 + timedelta(days=1)

    # temperature calculation
    T_history = np.array(
        [*np.linspace(cWR.temp_min, cWR.temp_max, num=int((noonTime - currSunriseDate) / stepTimeDelta))[0:-1],
         *np.linspace(cWR.temp_max, nextWR.temp_min, num=int((nextSunriseDate - noonTime) / stepTimeDelta) + 2)]
    )
    timeHistory = [currSunriseDate + stepTimeDelta * i for i in range(0, len(T_history))]

    prec_history = Precipitation.get_precipitation_history(cWR.prec, T_history)

    ##############################################################################
    # ------------------------------ day step (Delta loop) -----------------------
    ##############################################################################
    for c_date_time, T_curr, prec_curr in zip(timeHistory, T_history, prec_history):
        pretty_print('%s' % c_date_time.strftime("%B-%d-%Y %H:%M:%S"))

        ##########################################################################
        # ------------------------- Ежедневные операции --------------------------
        ##########################################################################
        if c_date_time.second / 60 == timeForDailyOperation.seconds / 60:
            # Утренние технологические операции
            h_running_controller.technology_descriptor.Irrigation_Regime.stepoAct(h_running_controller.agro_eco_system)
            h_running_controller.technology_descriptor.Fertilization_Regime.stepoAct(
                h_running_controller.agro_eco_system)
            h_running_controller.technology_descriptor.Soil_Tillage_Regime.stepoAct(
                h_running_controller.agro_eco_system)
        else:
            print("Not now")

        ##########################################################################
        # ------------------------- Расчет баланса снега -------------------------
        ##########################################################################
        # Семантические операции
        if (T_curr < 0):  # Если текущая температура < 0 - количество снега увеличивается
            sum_snow = sum_snow + prec_curr
            h_running_controller.agro_eco_system.air_part.alpha_snow = 0
        else:  # Иначе считаем таяние снега и прибавляем осадки
            del_snow_prec = popov_melting(h_running_controller.agro_eco_system, c_date_time, stepTimeDelta,
                                          T_curr)  # Проверить формулу Попова
            print(c_date_time)
            prec_curr += del_snow_prec
            sum_snow = sum_snow - del_snow_prec

        ##########################################################################
        # ---- Радиация и фотосинтез(с потенциальным сопротивлением устьиц) ------
        ##########################################################################
        # Запоминаем приходящщу радиацию
        # Запоминаем почвенну радиацию
        # RadPhotosynthesis(hRunningController.agroEcoSystem, False)#TODO
        h_running_controller.agro_eco_system.air_part.SumRad = get_curr_sum_rad(fi, c_date_time, stepTimeDelta)
        # ---------------------------- get Kex from df -------------------------------------
        try:
            curKex = float(
                h_running_controller.weather_df
                [h_running_controller.weather_df['Date'] == c_date_time.strftime("%d/%m/%Y")]
                ['Kex']
            )
        except Exception:
            curKex = float(
                h_running_controller.weather_df
                [h_running_controller.weather_df['Date'] == (c_date_time - timedelta(days=1)).strftime("%d/%m/%Y")]
                ['Kex']
            )
        # -----------------------------------------------------------------------------------
        calculate_balance(
            air_part=h_running_controller.agro_eco_system.air_part,
            Rs=h_running_controller.agro_eco_system.air_part.SumRad,
            Kex=curKex,
            LAI=h_running_controller.agro_eco_system.crop_part.individual_plant.shoot.leaf.lai,
            T_curr=T_curr,
            delta_step=stepTimeDelta,
            ph_time=h_running_controller.agro_eco_system.crop_part.individual_plant.ph_time
        )

        ##########################################################################
        # --------------------- Водные потоки.Транспирация -----------------------
        ##########################################################################
        evapo_transpiration(h_running_controller.agro_eco_system)

        soil_temperature(
            cSystem=h_running_controller.agro_eco_system,
            T_curr=T_curr
        )

        ##########################################################################
        # ---------------------Расчет сумм осадков и транспирации ---------------- # TODO next step
        ##########################################################################
        print("Some simple calculation without functions calls")

        h_running_controller.agro_eco_system.air_part.sumTrans = h_running_controller.agro_eco_system.air_part.sum_trans \
                                                                 + h_running_controller.agro_eco_system.crop_part.eplant \
                                                                 + h_running_controller.agro_eco_system.crop_part.esoil

        h_running_controller.agro_eco_system.air_part.sumPrec = h_running_controller.agro_eco_system.air_part.sum_prec \
                                                                + cWR.prec \
                                                                + cWR.watering

        # Водные потоки в почве
        if (Tave >= 0):
            water_soil_dynamics(h_running_controller.agro_eco_system)
        else:
            print("RecalculateSoilNitrogen was't called (Tave = %d)" % (Tave))

        # Радиация и фотосинтез(с реальным сопротивлением устьиц)
        # RadPhotosynthesis(hRunningController.agroEcoSystem, True)

        # Развитие
        recalculate_bio_time(h_running_controller.agro_eco_system)

        # Почвенно - азотный блок
        if (Tave >= 0) and (sum_snow < 1):
            recalculate_soil_nitrogen(h_running_controller.agro_eco_system)
        else:
            print("RecalculateSoilNitrogen was't called(Tave = %d, sum_snow = %d)" % (Tave, sum_snow))

        # Рост.Распределение ассимилятов
        if h_running_controller.agro_eco_system.crop_part.individual_plant.ifase > 1:
            growth(h_running_controller.agro_eco_system)
        else:
            print("Growth was't called(Ifase = %d)" % (
                h_running_controller.agro_eco_system.crop_part.individual_plant.ifase))

        # Освежение динамических переменных
        h_running_controller.agro_eco_system.refreshing()
        h_running_controller.agro_eco_system.air_part.sum_snow = sum_snow

        # Его присвоение
        h_running_controller.agro_eco_system.air_part.currentEnv = cWR
        bTime = h_running_controller.agro_eco_system.crop_part.individual_plant.ph_time

        ##########################################################################
        # ------------------------------ weather history -------------------------
        ##########################################################################
        historyDict['weather'] = historyDict['weather'].append(
            pd.DataFrame(
                {
                    "Date": [c_date_time],
                    "T": [T_curr],
                    "Rad": [
                        h_running_controller.agro_eco_system.air_part.SumRad * 10_000 / stepTimeDelta.seconds],
                    "Prec": [prec_curr],
                    "sum_snow": [sum_snow],
                    "Rnl": [h_running_controller.agro_eco_system.air_part.Rnl],
                    "Rn": [h_running_controller.agro_eco_system.air_part.Rn],
                    "G": [h_running_controller.agro_eco_system.air_part.G]
                }
            )
        )
        ##########################################################################
        # ------------------------------ soil history ----------------------------
        ##########################################################################
        t = []
        T = np.zeros(len(h_running_controller.agro_eco_system.soil_part.soil_layers))
        layers = list(range(len(T)))
        for i, layer in enumerate(h_running_controller.agro_eco_system.soil_part.soil_layers):
            t.append(c_date_time)
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
        c_date_time += stepTimeDelta


def continous_running(hRunningController: TRunController):
    # Организация цикла по суточным шагам

    historyDict = {
        'weather': pd.DataFrame(
            {
                "Date": np.empty(0),
                "T": np.empty(0),
                "Rad": np.empty(0),
                "Prec": np.empty(0),
                "sum_snow": np.empty(0),
                "Rnl": np.empty(0),
                "Rn": np.empty(0),
                "G": np.empty(0)
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
    weatherIter = iter(hRunningController.weather_df.to_dict(orient='records'))
    weatherIter.__next__()
    for cWR in hRunningController.weather_df.to_dict(orient='records'):

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
    show_day_num = int(len(historyDict['soil']) * 10 / len(hRunningController.weather_df))
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

    continous_running(hRunningController=hRunningController)


if __name__ == '__main__':
    main()
