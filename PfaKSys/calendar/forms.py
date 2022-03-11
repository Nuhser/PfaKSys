from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from PfaKSys.calendar.sync_interval import SyncInterval


class CalendarSettingsForm(FlaskForm):
    sync_interval = SelectField(lazy_gettext('ui.system_settings.calendar_sync_interval'), choices=[(sync_interval.name, sync_interval.value) for sync_interval in SyncInterval])
    submit_calendar_settings = SubmitField(lazy_gettext('ui.common.save'))