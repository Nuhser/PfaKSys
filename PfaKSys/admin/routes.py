from flask import abort, Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required

from PfaKSys.admin.forms import MailSettingsForm
from PfaKSys.admin.utils import save_mail_settings
from PfaKSys.models import User, UserGroup


admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin():
        abort(403)

    mail_form = MailSettingsForm()

    if 'use_tls' in request.form:
        if mail_form.validate_on_submit():
            save_mail_settings(mail_form)

            flash(gettext('flash.success.system_settings.mail_saved'), 'success')
            redirect(url_for('main.settings'))

    elif request.method == 'GET':
        mail_form.server.data = current_app.config['MAIL_SERVER'] if 'MAIL_SERVER' in current_app.config else None
        mail_form.port.data = current_app.config['MAIL_PORT'] if 'MAIL_PORT' in current_app.config else None
        mail_form.use_tls.data = current_app.config['MAIL_USE_TLS'] if 'MAIL_USE_TLS' in current_app.config else None
        mail_form.sender.data = current_app.config['MAIL_SENDER'] if 'MAIL_SENDER' in current_app.config else None

    return render_template('admin/settings.html', title=gettext('page.system_settings.title'), mail_form=mail_form)


@admin_blueprint.route('/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    if not current_user.is_admin():
        abort(403)

    users = User.query.order_by(User.username.collate('NOCASE').asc()).all()
    user_groups = UserGroup.query.order_by(UserGroup.name.collate('NOCASE').asc()).all()

    user_tab_active = True

    return render_template('admin/user_management.html', title=gettext('page.user_management.title'), users=users, user_groups=user_groups, user_tab_active=user_tab_active)