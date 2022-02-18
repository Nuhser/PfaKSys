from calendar import monthrange
from datetime import datetime
from flask_babel import lazy_gettext
from sqlalchemy import true


class Calendar():
    def __init__(self, year: int, month: int) -> None:
        self.year = year
        self.month = Month(year, month)
        self.today = datetime.now()

    @staticmethod
    def from_datetime(date: datetime):
        return Calendar(date.year, date.month)


class Month():
    NAMES = [
        lazy_gettext('main.calendar.january'),
        lazy_gettext('main.calendar.february'),
        lazy_gettext('main.calendar.march'),
        lazy_gettext('main.calendar.april'),
        lazy_gettext('main.calendar.may'),
        lazy_gettext('main.calendar.june'),
        lazy_gettext('main.calendar.july'),
        lazy_gettext('main.calendar.august'),
        lazy_gettext('main.calendar.september'),
        lazy_gettext('main.calendar.october'),
        lazy_gettext('main.calendar.november'),
        lazy_gettext('main.calendar.december')
    ]

    def __init__(self, year: int, month: int) -> None:
        self.name = self.NAMES[month-1]
        self.number = month
        self.num_days = monthrange(year, month)[1]
        self.first_day = monthrange(year, month)[0]
        self.weeks = self._get_weeks(self.num_days, self.first_day, year, month)

    def _get_weeks(self, num_days: int, first_day: int, year: int, month: int) -> list:
        weeks = [[]]
        curr_day = 1
        curr_weekday = first_day

        if first_day != 0:
            last_num_days = monthrange(year if month > 1 else year-1, month-1 if month > 1 else 12)[1]

            for weekday, date in enumerate(range(last_num_days-first_day+1, last_num_days+1)):
                weeks[-1].append(Day(date, weekday, True))

        while curr_day <= num_days:
            if curr_weekday == 0:
                weeks.append([])

            weeks[-1].append(Day(curr_day, curr_weekday))
            curr_day += 1
            curr_weekday += 1

            if curr_weekday > 6:
                curr_weekday = 0

        curr_weekday -= 1
        if curr_weekday < 0:
            curr_weekday = 6

        for date in range(0, 6-curr_weekday):
            weeks[-1].append(Day(date+1, curr_weekday+date, True))

        return weeks


class Day():
    NAMES = [
        lazy_gettext('main.calendar.monday'),
        lazy_gettext('main.calendar.tuesday'),
        lazy_gettext('main.calendar.wednesday'),
        lazy_gettext('main.calendar.thursday'),
        lazy_gettext('main.calendar.friday'),
        lazy_gettext('main.calendar.saturday'),
        lazy_gettext('main.calendar.sunday')
    ]

    def __init__(self, date: int, weekday: int, other_month: bool=False) -> None:
        self.date = date
        self.weekday = weekday
        self.name = self.NAMES[weekday]
        self.other_month = other_month
