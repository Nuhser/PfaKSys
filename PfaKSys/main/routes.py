from datetime import datetime
from flask import Blueprint, render_template, request
from flask_babel import gettext
from flask_login import login_required

from PfaKSys.main.calendar import Calendar


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/about')
def about():
    return render_template('main/about.html', title=gettext('ui.common.about'))


@main_blueprint.route('/calendar')
@login_required
def calendar():
    month = request.args.get('month', None, type=int)
    year = request.args.get('year', None, type=int)

    if month == 0:
        month = 12
        year -= 1
    elif month == 13:
        month = 1
        year += 1

    date = datetime.now() if (month == None or year == None) else datetime(year, month, 1)

    calendar = Calendar.from_datetime(date)

    return render_template('main/calendar.html', title=gettext('page.calendar.title'), calendar=calendar)


@main_blueprint.route('/')
@main_blueprint.route('/home')
def home():
    return render_template('main/home.html', title=gettext('page.home.title'))
