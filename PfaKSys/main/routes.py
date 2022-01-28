from flask import abort, Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required

from PfaKSys.main.forms import MailSettingsForm
from PfaKSys.main.utils import save_mail_settings


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/about')
def about():
    return render_template('main/about.html', title=gettext('ui.common.about'))


@main_blueprint.route('/')
@main_blueprint.route('/home')
def home():
    return render_template('main/home.html', title=gettext('page.home.title'))


@main_blueprint.route('/settings', methods=['GET', 'POST'])
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

    return render_template('main/settings.html', title=gettext('page.system_settings.title'), mail_form=mail_form)
