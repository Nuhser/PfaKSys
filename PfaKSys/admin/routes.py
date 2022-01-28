import os

from flask import abort, Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required
from sqlalchemy import or_

from PfaKSys import db
from PfaKSys.admin.forms import MailSettingsForm, SearchUserForm, SearchUserGroupForm
from PfaKSys.admin.utils import save_mail_settings
from PfaKSys.models import User, UserGroup


admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/admin/delete_account/<int:user_id>', methods=['POST'])
@login_required
def delete_account(user_id):
    if not current_user.is_admin():
        abort(403)

    user = User.query.get_or_404(user_id)

    # delete profile picture
    if( user.image_file != 'default.jpg'):
        image_path = os.path.join(current_app.root_path, 'static/profile_pics', user.image_file)
        if os.path.isfile(image_path):
            os.remove(image_path)

    # delete user and settings
    db.session.delete(user.settings)
    db.session.delete(user)
    db.session.commit()

    current_app.logger.warning(f'Account {user.username} was deleted by admin { current_user.username }.')
    flash(gettext('flash.success.admin.account_deleted', username=user.username), 'success')
    return redirect(url_for('admin.user_management'))


@admin_blueprint.route('/admin/delete_user_group/<int:group_id>', methods=['POST'])
@login_required
def delete_user_group(group_id):
    if not current_user.is_admin():
        abort(403)

    group = UserGroup.query.get_or_404(group_id)

    if group.name == 'admin':
        flash(gettext('flash.warning.admin.cant_delete_admin_group'), 'warning')
        return redirect(url_for('admin.user_management'))

    db.session.delete(group)
    db.session.commit()

    current_app.logger.warning(f'User group {group.name} was deleted by admin { current_user.username }.')
    flash(gettext('flash.success.admin.user_group_deleted', group_name=group.name), 'success')
    return redirect(url_for('admin.user_management'))


@admin_blueprint.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin():
        abort(403)

    mail_form = MailSettingsForm()

    if 'use_tls' in request.form:
        if mail_form.validate_on_submit():
            save_mail_settings(mail_form)

            flash(gettext('flash.success.system_settings.mail_saved'), 'success')
            return redirect(url_for('admin.settings'))

    elif request.method == 'GET':
        mail_form.server.data = current_app.config['MAIL_SERVER'] if 'MAIL_SERVER' in current_app.config else None
        mail_form.port.data = current_app.config['MAIL_PORT'] if 'MAIL_PORT' in current_app.config else None
        mail_form.use_tls.data = current_app.config['MAIL_USE_TLS'] if 'MAIL_USE_TLS' in current_app.config else None
        mail_form.sender.data = current_app.config['MAIL_SENDER'] if 'MAIL_SENDER' in current_app.config else None

    return render_template('admin/settings.html', title=gettext('page.system_settings.title'), mail_form=mail_form)


@admin_blueprint.route('/admin/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    if not current_user.is_admin():
        abort(403)

    search_user_form = SearchUserForm()
    search_group_form = SearchUserGroupForm()

    if 'username' in request.form:
        if search_user_form.validate_on_submit():
            return redirect(url_for('admin.user_management', username=search_user_form.username.data))
    elif 'group_name' in request.form:
        if search_group_form.validate_on_submit():
            return redirect(url_for('admin.user_management', group_name=search_group_form.group_name.data))

    username = request.args.get('username', '', type=str)
    group_name = request.args.get('group_name', '', type=str)

    if (username == None) or (username == ''):
        users = User.query.order_by(User.username.collate('NOCASE').asc()).all()
    else:
        search_user_form.username.data = username
        users = User.query.filter(or_(User.username.contains(username), User.full_name.contains(username), User.email.contains(username))).order_by(User.username.collate('NOCASE').asc()).all()

    if (group_name == None) or (group_name == ''):
        user_groups = UserGroup.query.order_by(UserGroup.name.collate('NOCASE').asc()).all()
    else:
        search_group_form.group_name.data = group_name
        user_groups = UserGroup.query.filter(UserGroup.name.contains(group_name)).order_by(UserGroup.name.collate('NOCASE').asc()).all()

    user_tab_active = (group_name == None) or (group_name == '')

    return render_template('admin/user_management.html',
                            title=gettext('page.user_management.title'),
                            search_user_form=search_user_form,
                            search_group_form=search_group_form,
                            users=users,
                            user_groups=user_groups,
                            user_tab_active=user_tab_active)