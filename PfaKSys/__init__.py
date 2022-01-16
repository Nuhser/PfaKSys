from flask import current_app, Flask, request
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from PfaKSys.config.config import Config, init_logging


init_logging()

babel = Babel()
bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

# login_manager.login_view = 'users.login'
# login_manager.login_message_category = 'info'


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'].keys())


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    app.logger.info('PfaKSys app created. Server is beeing started...')

    babel.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # from PfaKSys.errors.handlers import errors
    # from PfaKSys.main.routes import main
    # from PfaKSys.user.routes import users

    # app.register_blueprint(errors)
    # app.register_blueprint(main)
    # app.register_blueprint(users)

    app.logger.info('Server has been started successfully.')

    return app
