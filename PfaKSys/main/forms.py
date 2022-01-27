from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    # generel
    language = SelectField(lazy_gettext('ui.common.language'), validators=[DataRequired()])

    submit = SubmitField(lazy_gettext('ui.common.save'))
