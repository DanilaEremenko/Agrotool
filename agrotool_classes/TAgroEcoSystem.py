# TODO check classes
from agrotool_lib.DebugInspector import whoami
from .OwningElement import OwningElement


class TWeatherRecord():
    def __init__(self, owningElement, isSomething):
        self.date = owningElement.date
        self.Prec = 0  # precipitation
        self.Watering = 0
        self.OwningElement = OwningElement()
        self.Tmin = 0  # min temperature
        self.Tmax = 0  # max temperature
        self.Tave = owningElement.tave  # average temperature
        self.Kex = 0

    def Delete(self):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
        pass


class TAirPart():
    def __init__(self, currentEnv: TWeatherRecord):
        self.currentEnv = currentEnv
        self.sumSnow = 100  # TODO
        self.alpha_snow = 0
        self.sumTrans = 0
        self.sumPrec = 0


class TIndividualtPlant():
    def __init__(self):
        self.Ifase = 0
        self.Ph_Time = 0


class TCrop_Part():
    def __init__(self):
        self.Esoil = 0
        self.Eplant = 0
        self.Individual_Plant = TIndividualtPlant()


class TAgroEcoSystem():
    def __init__(self, Air_Part: TAirPart):
        self.Air_Part = Air_Part
        self.Crop_Part = TCrop_Part()

    def refreshing(self):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
        pass
