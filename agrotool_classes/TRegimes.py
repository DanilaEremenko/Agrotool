# TODO check classes
from agrotool_lib.DebugInspector import whoami


class TRegime():
    def __init__(self):
        pass

    def stepoAct(self, agroEcoSystem):
        raise Exception("Need to be overridden")


class TIrrigation_Regime(TRegime):
    def __init__(self):
        super().__init__()

    def stepoAct(self, agroEcoSystem):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))


class TFertilization_Regime(TRegime):
    def __init__(self):
        super().__init__()

    def stepoAct(self, agroEcoSystem):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))


class TSoil_Tillage_Regime(TRegime):
    def __init__(self):
        super().__init__()

    def stepoAct(self, agroEcoSystem):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))


class THarvesting_Regime(TRegime):
    def __init__(self):
        super().__init__()

    def stepoAct(self, agroEcoSystem):
        print("%s.%s is a stub" % (type(self).__name__, whoami()))
