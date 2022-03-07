from flask import Blueprint, render_template
from flask_babel import gettext


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/about')
def about():
    return render_template('main/about.html', title=gettext('ui.common.about'))


@main_blueprint.route('/')
@main_blueprint.route('/home')
def home():
    return render_template('main/home.html', title=gettext('page.home.title'))
