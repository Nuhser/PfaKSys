from flask import current_app, Blueprint, render_template, request
from flask_babel import gettext
from flask_login import current_user


error_blueprint = Blueprint('error', __name__)


@error_blueprint.app_errorhandler(403)
def error_403(error):
    current_app.logger.warning(f'{current_user.username if current_user.is_authenticated else "An unknown user"} tried to access an URL their not authorized for: "{request.url}"')
    return render_template('errors/403.html', title=gettext('page.error_403.title'), debug_mode=current_app.debug, error=error), 403


@error_blueprint.app_errorhandler(404)
def error_404(error):
    current_app.logger.warning(f'{current_user.username if current_user.is_authenticated else "An unknown user"} tried to access an not existing URL: "{request.url}"')
    return render_template('errors/404.html', title=gettext('page.error_404.title'), debug_mode=current_app.debug, error=error), 404


@error_blueprint.app_errorhandler(405)
def error_405(error):
    current_app.logger.warning(f'{current_user.username if current_user.is_authenticated else "An unknown user"} tried to access the URL "{request.url}" by an unsupported method: "{request.method}"')
    return render_template('errors/405.html', title=gettext('page.error_405.title'), debug_mode=current_app.debug, error=error), 405


@error_blueprint.app_errorhandler(500)
def error_500(error):
    current_app.logger.error(f'An unexpected error occured while {current_user} tried to access a site:\n{error}')
    return render_template('errors/500.html', title=gettext('page.error_500.title'), debug_mode=current_app.debug, error=error), 500
