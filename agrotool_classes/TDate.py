from datetime import timedelta


class TDate():
    def __init__(self, day):
        self.date = timedelta(days=day, seconds=0, minutes=0, hours=0, weeks=0)

    def inc_day(self):
        self.date += timedelta(days=1)

    def __str__(self):
        return "%d" % self.date.days
