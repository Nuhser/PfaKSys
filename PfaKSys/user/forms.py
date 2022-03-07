from flask_babel import lazy_gettext
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from PfaKSys import bcrypt
from PfaKSys.models import User


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(lazy_gettext('ui.change_password.current_password'), validators=[DataRequired(), Length(8, 32)])
    new_password = PasswordField(lazy_gettext('ui.change_password.new_password'), validators=[DataRequired(), Length(8, 32)])
    confirm_new_password = PasswordField(lazy_gettext('ui.change_password.confirm_new_password'), validators=[DataRequired(), Length(8, 32), EqualTo('new_password')])
    submit_change_password = SubmitField(lazy_gettext('ui.password_reset.reset'))

    def validate_current_password(self, current_password: PasswordField) -> None:
        if not bcrypt.check_password_hash(current_user.password, current_password.data):
            raise ValidationError(lazy_gettext('validation_error.wrong_password'))

    def validate_new_password(self, new_password: PasswordField) -> None:
        password_string = new_password.data

        if (not any(c.islower() for c in password_string))\
            or (not any(c.isupper() for c in password_string))\
            or (not any(c.isdigit() for c in password_string))\
            or (not any(c.isalpha() for c in password_string)):
            raise ValidationError(lazy_gettext('validation_error.password_not_valid'))


class LoginForm(FlaskForm):
    username = StringField(lazy_gettext('ui.common.username'), validators=[DataRequired(), Length(2, 20)])
    password = PasswordField(lazy_gettext('ui.common.password'), validators=[DataRequired(), Length(8, 32)])

    remember = BooleanField(lazy_gettext('ui.login.remember_me'))

    submit = SubmitField(lazy_gettext('ui.common.login'))


class RegistrationForm(FlaskForm):
    username = StringField(lazy_gettext('ui.common.username'), validators=[DataRequired(), Length(2, 20)])
    full_name = StringField(lazy_gettext('ui.common.full_name'), validators=[DataRequired(), Length(2, 120)])
    email = StringField(lazy_gettext('ui.common.email'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('ui.common.password'), validators=[DataRequired(), Length(8, 32)])
    confirm_password = PasswordField(lazy_gettext('ui.common.confirm_password'), validators=[DataRequired(), Length(8, 32), EqualTo('password')])

    submit = SubmitField(lazy_gettext('ui.common.sign_up'))

    def validate_username(self, username: StringField) -> None:
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(lazy_gettext('validation_error.username_already_taken'))

    def validate_email(self, email: StringField) -> None:
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(lazy_gettext('validation_error.email_already_exists'))

    def validate_password(self, password: PasswordField) -> None:
        password_string = password.data

        if (not any(c.islower() for c in password_string))\
            or (not any(c.isupper() for c in password_string))\
            or (not any(c.isdigit() for c in password_string))\
            or (not any(c.isalpha() for c in password_string)):
            raise ValidationError(lazy_gettext('validation_error.password_not_valid'))


class RequestResetForm(FlaskForm):
    email = StringField(lazy_gettext('ui.common.email'), validators=[DataRequired(), Email()])
    submit = SubmitField(lazy_gettext('ui.password_reset.request'))

    def validate_email(self, email: StringField) -> None:
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError(lazy_gettext('validation_error.email_does_not_exist'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(lazy_gettext('ui.common.password'), validators=[DataRequired(), Length(8, 32)])
    confirm_password = PasswordField(lazy_gettext('ui.common.confirm_password'), validators=[DataRequired(), Length(8, 32), EqualTo('password')])

    submit = SubmitField(lazy_gettext('ui.password_reset.reset'))

    def validate_password(self, password: PasswordField) -> None:
        password_string = password.data

        if (not any(c.islower() for c in password_string))\
            or (not any(c.isupper() for c in password_string))\
            or (not any(c.isdigit() for c in password_string))\
            or (not any(c.isalpha() for c in password_string)):
            raise ValidationError(lazy_gettext('validation_error.password_not_valid'))


class UpdateAccountForm(FlaskForm):
    username = StringField(lazy_gettext('ui.common.username'), validators=[DataRequired(), Length(2, 20)])
    full_name = StringField(lazy_gettext('ui.common.full_name'), validators=[DataRequired(), Length(2, 120)])
    email = StringField(lazy_gettext('ui.common.email'), validators=[DataRequired(), Email()])
    picture = FileField(lazy_gettext('ui.account.profile_picture'), validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])

    submit = SubmitField(lazy_gettext('ui.common.update'))

    def validate_username(self, username: StringField) -> None:
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(lazy_gettext('validation_error.username_already_taken'))

    def validate_email(self, email: StringField) -> None:
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(lazy_gettext('validation_error.email_already_exists'))


class UserSettingsForm(FlaskForm):
    language = SelectField(lazy_gettext('ui.common.language'), validators=[DataRequired()])

    submit = SubmitField(lazy_gettext('ui.common.save'))
