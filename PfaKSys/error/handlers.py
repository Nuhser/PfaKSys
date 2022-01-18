from flask import current_app, Blueprint, render_template
from flask_babel import gettext


error_blueprint = Blueprint('error', __name__)


@error_blueprint.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title=gettext('page.error_403.title'), debug_mode=current_app.debug, error=error), 403


@error_blueprint.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title=gettext('page.error_404.title'), debug_mode=current_app.debug, error=error), 404


@error_blueprint.app_errorhandler(405)
def error_405(error):
    return render_template('errors/405.html', title=gettext('page.error_405.title'), debug_mode=current_app.debug, error=error), 405


@error_blueprint.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title=gettext('page.error_500.title'), debug_mode=current_app.debug, error=error), 500
