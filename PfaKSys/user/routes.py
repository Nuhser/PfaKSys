import os

from flask import abort, Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required, login_user, logout_user

from PfaKSys import bcrypt, db
from PfaKSys.main.email import send_email_to_all_admins
from PfaKSys.main.utils import get_system_settings, _url_for
from PfaKSys.models import User, UserGroup, UserSettings
from PfaKSys.user.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm, UserSettingsForm
from PfaKSys.user.utils import generate_and_save_gravatar, save_picture, send_reset_email


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')

    if form.validate_on_submit():
        old_username = current_user.username

        if form.picture.data:
            old_image_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
            if (current_user.image_file != 'default.jpg') and os.path.isfile(old_image_path):
                os.remove(old_image_path)

            current_user.image_file =  save_picture(form.picture.data)

        current_user.username = form.username.data
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        db.session.commit()

        if old_username != current_user.username:
            current_app.logger.info(f'{old_username} changed their name to {current_user.username}.')

        flash(gettext('flash.success.account_update'), 'success')
        return redirect(_url_for('user.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email

    return render_template('user/account.html', title=gettext('ui.common.account'), image_file=image_file, form=form)


@user_blueprint.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    logout_user()

    # delete profile picture
    if( user.image_file != 'default.jpg'):
        image_path = os.path.join(current_app.root_path, 'static/profile_pics', user.image_file)
        if os.path.isfile(image_path):
            os.remove(image_path)

    # delete user and settings
    db.session.delete(user.settings)
    db.session.delete(user)
    db.session.commit()

    current_app.logger.info(f'{user.username} deleted their account.')
    flash(gettext('flash.success.delete_account'), 'success')
    return redirect(_url_for('main.home'))


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(_url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            current_app.logger.info(f'{user.username} logged in successfully.')

            next_page = request.args.get('next')
            return redirect(next_page if next_page else _url_for('main.home'))
        else:
            flash(gettext('flash.danger.login_failed'), 'danger')

    return render_template('user/login.html', title=gettext('ui.common.login'), form=form)


@user_blueprint.route('/logout')
def logout():
    username = current_user.username

    logout_user()

    current_app.logger.info(f'{username} logged out successfully.')
    flash(gettext('flash.success.logout'), 'success')
    return redirect(_url_for('main.home'))


@user_blueprint.route('/modify_item_filters')
def modify_item_filters():
    filter_name = request.args.get('name', type=str)
    filter_conditions = request.args.getlist('conditions', type=str)
    filter_categories = request.args.getlist('categories', type=int)
    filter_locations = request.args.getlist('locations', type=int)

    # save current item filters
    current_user.settings.item_filters = {
        'name': filter_name,
        'conditions': filter_conditions,
        'categories': filter_categories,
        'locations': filter_locations
    }
    db.session.commit()

    return redirect(_url_for('item.overview'))


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(_url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        image_file = generate_and_save_gravatar(form.email.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # create user
        user = User(username=form.username.data, full_name=form.full_name.data, email=form.email.data, password=hashed_password, image_file=image_file)
        db.session.add(user)

        # give user settings
        user_settings = UserSettings(language=request.accept_languages.best_match(current_app.config['LANGUAGES'].keys()))
        user.settings = user_settings

        # make user admin if first user
        if len(User.query.all()) == 1:
            user.groups.append(UserGroup.query.filter_by(name='admin').first())

        db.session.commit()

        if get_system_settings().notifications['NEW_USER']:
            send_email_to_all_admins(
                subject=gettext('mail.new_user_admin.subject', username=user.username),
                body=gettext('mail.new_user_admin.body', username=user.username, full_name=user.full_name, email=user.email, link=_url_for('admin.edit_user', user_id=user.id))
            )

        current_app.logger.info(f'New user {user.username} was created successfully.')
        flash(gettext('flash.success.account_created'), 'success')
        return redirect(_url_for('user.login'))

    return render_template('user/register.html', title=gettext('ui.common.sign_up'), form=form)


@user_blueprint.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(_url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        try:
            send_reset_email(user)
        except Exception:
            current_app.logger.exception(f'The connection to \'{current_app.config["MAIL_SERVER"]}\' got refused while {user.username} tried to reset their password.')
            abort(500)

        current_app.logger.warning(f'{user.username} has requested an email to reset their password.')
        flash(gettext('flash.info.reset_email_send'), 'info')
        return redirect(_url_for('user.login'))

    return render_template('user/request_reset.html', title=gettext('page.reset_password.title'), form=form)


@user_blueprint.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(_url_for('main.home'))

    user = User.verify_reset_token(token)
    if not user:
        current_app.logger.warning(f'Invalid or expired token was used to try to reset a password! (Token: {token})')
        flash(gettext('flash.warning.reset_token_expired_or_invalid'), 'warning')
        return redirect(_url_for('user.request_reset'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        current_app.logger.info(f'{user.username} has reset their password.')
        flash(gettext('flash.success.password_reset'), 'success')
        return redirect(_url_for('user.login'))

    return render_template('user/reset_password.html', title=gettext('page.reset_password.title'), form=form)


@user_blueprint.route('/user_settings', methods=['GET', 'POST'])
@login_required
def settings():
    # initialize form
    form = UserSettingsForm()
    form.language.choices = [(key, value) for key, value in current_app.config['LANGUAGES'].items()]

    # validate submitted form
    if form.validate_on_submit():
        current_user.settings.language = form.language.data
        db.session.commit()

        flash(gettext('flash.success.user_settings_saved'), 'success')
        return redirect(_url_for('user.settings'))

    # fill form with current values if settings are opened
    elif request.method == 'GET':
        form.language.data = current_user.settings.language

    return render_template('user/settings.html', title=gettext('page.user_settings.title'), form=form)
