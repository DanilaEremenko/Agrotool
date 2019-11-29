class TWeatherHistory():
    def __init__(self):
        self.tList = []
        self.kList = []
        self.dayList = []
        self.deltaList = []

    def append(self, anotherHistory):
        self.tList.append(anotherHistory.tList)
        self.kList.append(anotherHistory.kList)
        self.dayList.append(anotherHistory.dayList)
        self.deltaList.append(anotherHistory.deltaList)
