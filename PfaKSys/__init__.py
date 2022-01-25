import os

from flask import current_app, Flask, request
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_login import current_user, LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from PfaKSys.config.config import Config, init_logging


init_logging()

# set SQL naming conventions
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)

# initialize flask extensions
babel = Babel()
bcrypt = Bcrypt()
db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

# configure login manager
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'


# define babel locale selector
@babel.localeselector
def get_locale():
    if current_user.is_authenticated:
        return current_user.settings.language

    else:
        return request.accept_languages.best_match(current_app.config['LANGUAGES'].keys())


def create_app(config=Config):
    # create flask app
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_json(os.path.join(app.root_path, 'config/ini.json'))

    app.logger.info('PfaKSys app created. Server is beeing started...')

    # set app for extensions
    babel.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # create database and basic groups if not existing
    if not os.path.isfile(os.path.join(app.root_path, 'db.sqlite')):
        from PfaKSys.models import Item, ItemCategory, ItemLocation, User, UserGroup, UserSettings
        with app.app_context():
            db.create_all()
            db.session.add(UserGroup(name='admin'))
            db.session.commit()

    # import and register blueprints
    from PfaKSys.error.handlers import error_blueprint
    from PfaKSys.item.routes import item_blueprint
    from PfaKSys.main.routes import main_blueprint
    from PfaKSys.user.routes import user_blueprint

    app.register_blueprint(error_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_blueprint)

    app.logger.info('Server has been started successfully.')

    return app
