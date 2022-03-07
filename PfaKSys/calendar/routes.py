
from datetime import datetime
from flask import Blueprint, request
from flask_login import login_required

from PfaKSys.calendar.calendar import Calendar, Event


calendar_blueprint = Blueprint('calendar', __name__)


@calendar_blueprint.route('/calendar')
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

    events = Event.from_ical('https://hessenwiki.de/confluence/rest/calendar-services/1.0/calendar/export/subcalendar/private/acab0f6eb1ea9a4b0478f49b91b73d0095e1130d.ics', ["Schulferien & Feiertage"])
    print(len(events))

    return render_template('main/calendar.html', title=gettext('page.calendar.title'), calendar=calendar)