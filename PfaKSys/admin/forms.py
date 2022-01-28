from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired


class MailSettingsForm(FlaskForm):
    server = StringField(lazy_gettext('ui.system_settings.mail_server'), validators=[DataRequired()])
    port = IntegerField(lazy_gettext('ui.system_settings.mail_port'), validators=[DataRequired()], default=587)
    use_tls = BooleanField(lazy_gettext('ui.system_settings.mail_use_tls'), validators=[DataRequired()], default=True)
    sender = StringField(lazy_gettext('ui.system_settings.mail_sender'), validators=[DataRequired()])

    submit = SubmitField(lazy_gettext('ui.common.save'))


class SearchUserForm(FlaskForm):
    username = StringField(lazy_gettext('ui.common.username'))
    submit = SubmitField(lazy_gettext('ui.common.search'))


class SearchUserGroupForm(FlaskForm):
    group_name = StringField(lazy_gettext('ui.admin.group_name'))
    submit = SubmitField(lazy_gettext('ui.common.search'))
