from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError

from PfaKSys.models import User, UserGroup


class DatabaseSettingsForm(FlaskForm):
    database_backup_quantity = IntegerField(lazy_gettext('ui.system_settings.database_backup_quantity'), validators=[DataRequired(), NumberRange(min=1, max=14)])    
    submit = SubmitField(lazy_gettext('ui.common.save'))


class EditAccountFormBase(FlaskForm):
    username = StringField(lazy_gettext('ui.common.username'), validators=[DataRequired(), Length(2, 20)])
    full_name = StringField(lazy_gettext('ui.common.full_name'), validators=[DataRequired(), Length(2, 120)])
    email = StringField(lazy_gettext('ui.common.email'), validators=[DataRequired(), Email()])
    picture = FileField(lazy_gettext('ui.account.profile_picture'), validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])

    submit = SubmitField(lazy_gettext('ui.common.save'))

    user = None

    def validate_username(self, username: StringField) -> None:
        if username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(lazy_gettext('validation_error.username_already_taken'))

    def validate_email(self, email: StringField) -> None:
        if email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(lazy_gettext('validation_error.email_already_exists'))

def edit_account_form_builder(user_groups):
    class EditAccountForm(EditAccountFormBase):
        pass

    for user_group in user_groups:
        setattr(EditAccountForm, f'group_{user_group.id}', BooleanField(label=user_group.name))

    return EditAccountForm()


class MailSettingsForm(FlaskForm):
    server = StringField(lazy_gettext('ui.system_settings.mail_server'), validators=[DataRequired()])
    port = IntegerField(lazy_gettext('ui.system_settings.mail_port'), validators=[DataRequired()], default=587)
    use_tls = BooleanField(lazy_gettext('ui.system_settings.mail_use_tls'), default=True)
    use_ssl = BooleanField(lazy_gettext('ui.system_settings.mail_use_ssl'), default=True)
    mail_sender = StringField(lazy_gettext('ui.system_settings.mail_sender'), validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('ui.common.save'))


class SearchUserForm(FlaskForm):
    username = StringField(lazy_gettext('ui.common.username'))
    submit = SubmitField(lazy_gettext('ui.common.search'))


class SearchUserGroupForm(FlaskForm):
    group_name = StringField(lazy_gettext('ui.admin.group_name'))
    submit = SubmitField(lazy_gettext('ui.common.search'))


class UserGroupForm(FlaskForm):
    name = StringField(lazy_gettext('ui.admin.group_name'), validators=[DataRequired(), Length(max=32)])
    manage_material_permission = BooleanField(lazy_gettext('main.permissions.manage_material'), default=False)
    manage_categories_permission = BooleanField(lazy_gettext('main.permissions.manage_categories'), default=False)
    manage_locations_permission = BooleanField(lazy_gettext('main.permissions.manage_locations'), default=False)
    submit = SubmitField(lazy_gettext('ui.common.save'))

    group = None

    def validate_name(self, name: StringField) -> None:
        if (self.group == None) or (name.data != self.group.name):
            group = UserGroup.query.filter_by(name=name.data).first()
            if group:
                raise ValidationError(lazy_gettext('validation_error.group_name_already_taken'))
