from flask import current_app, Blueprint, render_template


error_blueprint = Blueprint('error', __name__)


@error_blueprint.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', debug_mode=current_app.debug, error=error), 403


@error_blueprint.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', debug_mode=current_app.debug, error=error), 404


@error_blueprint.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', debug_mode=current_app.debug, error=error), 500
