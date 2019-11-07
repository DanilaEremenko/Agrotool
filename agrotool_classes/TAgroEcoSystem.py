# TODO check classes

from .OwningElement import OwningElement


class TWeatherRecord():
    def __init__(self, owningElement, isSomething):
        self.date = owningElement.date
        self.tave = owningElement.tave
        self.prec = 0
        self.Watering = 0
        self.OwningElement = OwningElement()
        self.Tmin = 0
        self.Tmax = 0
        self.Kex = 0

    def Delete(self):
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
        pass
