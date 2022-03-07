from enum import Enum
import icalendar
import urllib.request

from calendar import monthrange
from datetime import datetime, timedelta, timezone
from dateutil.rrule import *
from flask_babel import lazy_gettext


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
        lazy_gettext('calendar.month.january'),
        lazy_gettext('calendar.month.february'),
        lazy_gettext('calendar.month.march'),
        lazy_gettext('calendar.month.april'),
        lazy_gettext('calendar.month.may'),
        lazy_gettext('calendar.month.june'),
        lazy_gettext('calendar.month.july'),
        lazy_gettext('calendar.month.august'),
        lazy_gettext('calendar.month.september'),
        lazy_gettext('calendar.month.october'),
        lazy_gettext('calendar.month.november'),
        lazy_gettext('calendar.month.december')
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
        lazy_gettext('calendar.weekday.monday'),
        lazy_gettext('calendar.weekday.tuesday'),
        lazy_gettext('calendar.weekday.wednesday'),
        lazy_gettext('calendar.weekday.thursday'),
        lazy_gettext('calendar.weekday.friday'),
        lazy_gettext('calendar.weekday.saturday'),
        lazy_gettext('calendar.weekday.sunday')
    ]

    def __init__(self, date: int, weekday: int, other_month: bool=False) -> None:
        self.date = date
        self.weekday = weekday
        self.name = self.NAMES[weekday]
        self.other_month = other_month


class SyncInterval(Enum):
    pass


class Event():
    def __init__(self, date: datetime, title: str, description: str, location: str, date_end: datetime=None) -> None:
        self.date = date
        self.date_end = date_end
        self.title = title
        self.description = description if location != None else ''
        self.location = location if location != None else ''

    def __repr__(self) -> str:
        return f"Event('{self.title}', from: '{self.date}', to: '{self.date_end}', description: '{self.description}', location: '{self.location}')"


    @staticmethod
    def from_ical(url: str, categories_to_ignore: list[str]=[]) -> list:
        def parse_recurrences(recur_rule, start, exclusions) -> list:
            rules = rruleset()
            first_rule = rrulestr(recur_rule, dtstart=start)
            rules.rrule(first_rule)

            if not isinstance(exclusions, list):
                exclusions = [exclusions]
                for xdate in exclusions:
                    try:
                        rules.exdate(xdate.dts[0].dt)
                    except AttributeError:
                        pass

            dates = []
            for rule in rules:
                dates.append(rule.strftime("%D %H:%M UTC "))

            return dates

        with urllib.request.urlopen(url) as ical_file:
            gcal = icalendar.Calendar.from_ical(ical_file.read())

            events = []
            for component in gcal.walk():
                if (component.name == "VEVENT") and (not component.get('categories').cats[0] in categories_to_ignore):
                    summary = component.get('summary')
                    description = component.get('description')
                    location = component.get('location')
                    startdt = component.get('dtstart').dt
                    enddt = component.get('dtend').dt
                    exdate = component.get('exdate')

                    if component.get('rrule'):
                        reoccur = component.get('rrule').to_ical().decode('utf-8')
                        for date in parse_recurrences(reoccur, startdt, exdate):
                            events.append(Event(date, summary, description, location))
                    else:
                        events.append(Event(startdt, summary, description, location, date_end=enddt))

        return events


    def get_google_maps_link(self) -> str:
        return f'https://maps.google.com/?q={self.location}'
