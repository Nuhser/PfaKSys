import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required, login_user, logout_user

from PfaKSys import bcrypt, db
from PfaKSys.models import User, UserGroup
from PfaKSys.user.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm
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
            if (current_user.image_file != 'default.jpg') and os.path.exists(old_image_path):
                os.remove(old_image_path)

            current_user.image_file =  save_picture(form.picture.data)

        current_user.username = form.username.data
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        db.session.commit()

        if old_username != current_user.username:
            current_app.logger.info(f'{old_username} changed his/her name to {current_user.username}.')

        flash(gettext('flash.success.account_update'), 'success')
        return redirect(url_for('user.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email

    return render_template('user/account.html', title=gettext('ui.common.account'), image_file=image_file, form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            current_app.logger.info(f'{user.username} logged in successfully.')

            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.home'))
        else:
            flash(gettext('flash.danger.login_failed'), 'danger')

    return render_template('user/login.html', title=gettext('ui.common.login'), form=form)


@user_blueprint.route('/logout')
def logout():
    username = current_user.username

    logout_user()

    current_app.logger.info(f'{username} logged out successfully.')
    flash(gettext('flash.success.logout'), 'success')
    return redirect(url_for('main.home'))


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        image_file = generate_and_save_gravatar(form.email.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        default_usergroup = UserGroup.query.get(1)
        
        user = User(username=form.username.data, full_name=form.full_name.data, email=form.email.data, password=hashed_password, image_file=image_file, groups=[default_usergroup])
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f'New user {user.username} was created successfully.')
        flash(gettext('flash.success.account_created'), 'success')
        return redirect(url_for('user.login'))

    return render_template('user/register.html', title=gettext('ui.common.sign_up'), form=form)


@user_blueprint.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)

        current_app.logger.info(f'{user.username} has requested an email to reset their password.')
        flash(gettext('flash.info.reset_email_send'), 'info')
        return redirect(url_for('user.login'))

    return render_template('user/request_reset.html', title=gettext('page.reset_password.title'), form=form)


@user_blueprint.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    if not user:
        current_app.logger.warning(f'Invalid or expired token was used to try to reset a password! (Token: {token})')
        flash(gettext('flash.warning.reset_token_expired_or_invalid'), 'warning')
        return redirect(url_for('user.request_reset'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        current_app.logger.info(f'User {user.username} has reset their password.')
        flash(gettext('flash.success.password_reset'), 'success')
        return redirect(url_for('user.login'))

    return render_template('user/reset_password.html', title=gettext('page.reset_password.title'), form=form)
