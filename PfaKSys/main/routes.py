from flask import Blueprint, abort, redirect, render_template, url_for
from flask_babel import gettext
from flask_login import current_user, login_required

from PfaKSys.main.forms import SettingsForm


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

    form = SettingsForm()

    if form.validate_on_submit():
        redirect(url_for('main.settings'))

    return render_template('main/settings.html', title=gettext('page.system_settings.title'), form=form)
