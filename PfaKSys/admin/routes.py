import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_babel import gettext
from flask_login import current_user, login_required
from sqlalchemy import or_

from PfaKSys import db
from PfaKSys.admin.forms import DatabaseSettingsForm, edit_account_form_builder, MailSettingsForm, NotificationSettingsForm, SearchUserForm, SearchUserGroupForm, UserGroupForm
from PfaKSys.admin.utils import database_backup, save_database_settings, save_mail_settings, save_notification_settings
from PfaKSys.main.permissions import admin_required, Permission
from PfaKSys.main.utils import get_system_settings, _url_for
from PfaKSys.models import User, UserGroup
from PfaKSys.user.utils import save_picture


admin_blueprint = Blueprint('admin', __name__)
admin_blueprint.add_app_template_filter(Permission.from_str_list_to_value_list, 'permission_string_list')


@admin_blueprint.route('/admin/add_user_group', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user_group():
    form = UserGroupForm()

    if form.validate_on_submit():
        group = UserGroup(name=form.name.data)

        permissions = []
        if form.data_export_permission.data:
            permissions.append('data_export')
        if form.data_import_permission.data:
            permissions.append('data_import')
        if form.manage_material_permission.data:
            permissions.append('manage_material')
        if form.manage_categories_permission.data:
            permissions.append('manage_categories')
        if form.manage_locations_permission.data:
            permissions.append('manage_locations')
        group.permissions = ';'.join(permissions)

        db.session.add(group)
        db.session.commit()

        current_app.logger.info(f'{current_user.username} created the new user group "{group}"')
        flash(gettext('flash.success.admin.user_group_created', group_name=group.name), 'success')
        return redirect(_url_for('admin.user_management'))

    return render_template('admin/user_group.html', title=gettext('page.admin.user_group.title'), form=form)


@admin_blueprint.route('/admin/create_database_backup', methods=['POST'])
@login_required
@admin_required
def create_database_backup():
    new_backup_name = database_backup()

    current_app.logger.info(f'{current_user.username} created a new database backup "{new_backup_name}"')
    flash(gettext('flash.success.admin.database_backup_created', backup_name=new_backup_name), 'success')
    return redirect(_url_for('admin.settings'))


@admin_blueprint.route('/admin/delete_account/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_account(user_id):
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

    current_app.logger.info(f'Account "{user.username}" was deleted by admin {current_user.username}.')
    flash(gettext('flash.success.admin.account_deleted', username=user.username), 'success')
    return redirect(_url_for('admin.user_management'))


@admin_blueprint.route('/admin/delete_user_group/<int:group_id>', methods=['POST'])
@login_required
@admin_required
def delete_user_group(group_id):
    group = UserGroup.query.get_or_404(group_id)

    if group.name == 'admin':
        current_app.logger.warning(f'{current_user.name} tried to delete the admin group!')
        flash(gettext('flash.warning.admin.cant_delete_admin_group'), 'warning')
        return redirect(_url_for('admin.user_management'))

    db.session.delete(group)
    db.session.commit()

    current_app.logger.info(f'User group "{group.name}" was deleted by admin {current_user.username}.')
    flash(gettext('flash.success.admin.user_group_deleted', group_name=group.name), 'success')
    return redirect(_url_for('admin.user_management'))


@admin_blueprint.route('/admin/download_db_backup/<path:filename>')
@login_required
@admin_required
def download_db_backup(filename: str):
    db_backup_path = os.path.join(current_app.root_path, 'backups/db', filename)
    return send_file(db_backup_path)


@admin_blueprint.route('/admin/download_log/<path:filename>')
@login_required
@admin_required
def download_log(filename: str):
    log_path = os.path.join(current_app.root_path, 'logs', filename)
    return send_file(log_path)


@admin_blueprint.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    image_file = url_for('static', filename=f'profile_pics/{user.image_file}')

    form = edit_account_form_builder(group for group in UserGroup.query.all())
    form.user = user

    if form.validate_on_submit():
        old_username = user.username

        if form.picture.data:
            old_image_path = os.path.join(current_app.root_path, 'static/profile_pics', user.image_file)
            if (user.image_file != 'default.jpg') and os.path.isfile(old_image_path):
                os.remove(old_image_path)

            user.image_file = save_picture(form.picture.data)

        user.username = form.username.data
        user.full_name = form.full_name.data
        user.email = form.email.data

        user.groups = []
        for group_field in [key for key in form._fields if key.startswith('group_')]:
            if form._fields[group_field].data:
                user.groups.append(UserGroup.query.get(int(group_field.removeprefix('group_'))))

        db.session.commit()

        if old_username != user.username:
            current_app.logger.info(f'{current_user.username} edited the account/user groups of "{old_username}" and changed their username to "{user.username}".')
        else:
            current_app.logger.info(f'{current_user.username} edited the account/user groups of "{user.username}".')

        flash(gettext('flash.success.account_update_admin', username=user.username), 'success')
        return redirect(_url_for('admin.user_management'))

    elif request.method == 'GET':
        form.username.data = user.username
        form.full_name.data = user.full_name
        form.email.data = user.email

        for group_field in [key for key in form._fields if key.startswith('group_')]:
            form._fields[group_field].data = UserGroup.query.get(int(group_field.removeprefix('group_'))) in user.groups

    return render_template('admin/edit_user.html', title=gettext('page.admin.edit_user.title', username=user.username), form=form, user=user, image_file=image_file)


@admin_blueprint.route('/admin/edit_user_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_group(group_id):
    group = UserGroup.query.get_or_404(group_id)
    permissions = [Permission.from_str(p) for p in group.permissions.split(';')] if ((group.permissions != None) and (group.permissions != '')) else []
    form = UserGroupForm()
    form.group = group

    if form.validate_on_submit():
        old_group_name = group.name
        group.name = form.name.data

        permissions = []
        if form.data_export_permission.data:
            permissions.append('data_export')
        if form.data_import_permission.data:
            permissions.append('data_import')
        if form.manage_material_permission.data:
            permissions.append('manage_material')
        if form.manage_categories_permission.data:
            permissions.append('manage_categories')
        if form.manage_locations_permission.data:
            permissions.append('manage_locations')
        group.permissions = ';'.join(permissions)

        db.session.commit()

        if old_group_name != group.name:
            current_app.logger.info(f'{current_user.username} edited user group "{old_group_name}" and changed the name to "{group.name}".')
        else:
            current_app.logger.info(f'{current_user.username} edited user group "{group.name}".')

        flash(gettext('flash.success.admin.user_group_edited', group_name=group.name), 'success')
        return redirect(_url_for('admin.user_management'))

    elif request.method == 'GET':
        form.name.data = group.name
        form.data_export_permission.data = Permission.data_export in permissions
        form.data_import_permission.data = Permission.data_import in permissions
        form.manage_material_permission.data = Permission.manage_material in permissions
        form.manage_categories_permission.data = Permission.manage_categories in permissions
        form.manage_locations_permission.data = Permission.manage_locations in permissions

    return render_template('admin/user_group.html', title=gettext('page.admin.edit_user_group.title', group_name=group.name), form=form)


@admin_blueprint.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    system_settings = get_system_settings()

    database_form = DatabaseSettingsForm()
    mail_form = MailSettingsForm()
    notifications_form = NotificationSettingsForm()

    if 'mail_sender' in request.form:
        if mail_form.validate_on_submit():
            save_mail_settings(mail_form)

            current_app.logger.info(f'{current_user.username} edited the system settings (mail).')
            flash(gettext('flash.success.system_settings.mail_saved'), 'success')
            return redirect(_url_for('admin.settings'))

    elif 'database_backup_quantity' in request.form:
        if database_form.validate_on_submit():
            save_database_settings(database_form)

            current_app.logger.info(f'{current_user.username} edited the system settings (database).')
            flash(gettext('flash.success.system_settings.database_saved'), 'success')
            return redirect(_url_for('admin.settings'))

    elif 'submit_notification_settings' in request.form:
        if notifications_form.validate_on_submit():
            save_notification_settings(notifications_form)

            current_app.logger.info(f'{current_user.username} edited the system settings (notifications).')
            flash(gettext('flash.success.system_settings.notifications_saved'), 'success')
            return redirect(_url_for('admin.settings'))

    elif request.method == 'GET':
        database_form.database_backup_quantity.data = system_settings.database['BACKUP_QUANTITY']

        db_backups_path = os.path.join(current_app.root_path, 'backups/db')
        db_backups = sorted([file for file in os.listdir(db_backups_path) if os.path.isfile(os.path.join(db_backups_path, file))])

        mail_form.server.data = current_app.config['MAIL_SERVER'] if 'MAIL_SERVER' in current_app.config else None
        mail_form.port.data = current_app.config['MAIL_PORT'] if 'MAIL_PORT' in current_app.config else None
        mail_form.use_tls.data = current_app.config['MAIL_USE_TLS'] if 'MAIL_USE_TLS' in current_app.config else None
        mail_form.use_ssl.data = current_app.config['MAIL_USE_SSL'] if 'MAIL_USE_SSL' in current_app.config else None
        mail_form.mail_sender.data = current_app.config['MAIL_SENDER'] if 'MAIL_SENDER' in current_app.config else None

        notifications_form.new_user.data = system_settings.notifications["NEW_USER"]

        log_path = os.path.join(current_app.root_path, 'logs')
        logs = {
            file: [line.strip() for line in open(os.path.join(log_path, file), encoding='ISO-8859-1').readlines()]
            
            for file in os.listdir(log_path) if os.path.isfile(os.path.join(log_path, file))
        }
        logs = {file: logs[file] for file in sorted(logs.keys())}

    return render_template(
        'admin/settings.html',
        title=gettext('page.system_settings.title'),
        database_form=database_form,
        db_backups=db_backups,
        mail_form=mail_form,
        notifications_form=notifications_form,
        logs=logs
    )


@admin_blueprint.route('/admin/user_management', methods=['GET', 'POST'])
@login_required
@admin_required
def user_management():
    search_user_form = SearchUserForm()
    search_group_form = SearchUserGroupForm()

    if 'username' in request.form:
        if search_user_form.validate_on_submit():
            return redirect(_url_for('admin.user_management', username=search_user_form.username.data))
    elif 'group_name' in request.form:
        if search_group_form.validate_on_submit():
            return redirect(_url_for('admin.user_management', group_name=search_group_form.group_name.data))

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