from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class CalendarSettingsForm(FlaskForm):
    sync_interval = SelectField(lazy_gettext('ui.system_settings.calendar_sync_interval'), choices=[(condition.name, condition.value) for condition in ItemCondition])
    submit_calendar_settings = SubmitField(lazy_gettext('ui.common.save'))