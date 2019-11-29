from datetime import timedelta


class TDate():
    def __init__(self, seconds=0, minutes=0, hours=0, weeks=0, days=0):
        self.date = timedelta(seconds=seconds, minutes=minutes, hours=hours, weeks=weeks, days=days)

    def add_delta(self, delta):
        self.date += delta.date

    def __str__(self):
        return self.date.__str__()

    def get_hour(self):
        return int(self.date.seconds / 60 / 60)

    def get_day(self):
        return int(self.date.days)


if __name__ == '__main__':
    some_date = TDate(days=1)
    delta = TDate(hours=12)
    print(some_date)
    some_date.add_delta(delta)
    print(some_date)
    some_date.add_delta(delta)
    print(some_date)

    print("day = %d, hour = %d" % (some_date.get_day(), some_date.get_hour()))
