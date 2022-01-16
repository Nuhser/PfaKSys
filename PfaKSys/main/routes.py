from flask import Blueprint, render_template, request
from flask_babel import gettext


main = Blueprint('main', __name__)


@main.route('/about')
def about():
    return render_template('about.html', title=gettext('ui.common.about'))


@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title=gettext('page.home.title'))
