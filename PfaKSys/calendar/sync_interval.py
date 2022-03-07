from enum import Enum

from flask_babel import lazy_gettext


class SyncInterval(Enum):
    five_minutes = lazy_gettext('calendar.sync_interval.five_minutes')
    thirty_minutes = lazy_gettext('calendar.sync_interval.thirty_minutes')
    hourly = lazy_gettext('calendar.sync_interval.hourly')
    five_hours = lazy_gettext('calendar.sync_interval.five_hours')
    daily = lazy_gettext('calendar.sync_interval.daily')

    @classmethod
    def __dir__(cls) -> list:
        return list(sync_interval for sync_interval in cls)
