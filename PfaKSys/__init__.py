import atexit
import os

from flask import current_app, Flask, request
from flask_apscheduler import APScheduler
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_login import current_user, LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from PfaKSys.config.config import Config, init_logging, ProductionConfig, SQL_CONVENTIONS


init_logging()

# initialize flask extensions
babel = Babel()
bcrypt = Bcrypt()
db = SQLAlchemy(metadata=MetaData(naming_convention=SQL_CONVENTIONS))
login_manager = LoginManager()
mail = Mail()
scheduler = APScheduler()

# configure login manager
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'


# define babel locale selector
@babel.localeselector
def get_locale():
    if current_user.is_authenticated:
        return current_user.settings.language

    else:
        return request.accept_languages.best_match(current_app.config['LANGUAGES'].keys(), default=Config.BABEL_DEFAULT_LOCALE)


def create_app(config=ProductionConfig):
    # create flask app
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_json(os.path.join(app.root_path, 'config/custom_config.json'))

    app.logger.info('PfaKSys app created. Server is beeing started...')

    # set app for extensions
    babel.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)

    # create database if not existing
    if not os.path.isfile(os.path.join(app.root_path, 'db.sqlite')):
        from PfaKSys.models import Item, ItemCategory, ItemLocation, SystemSettings, User, UserGroup, UserSettings
        with app.app_context():
            db.create_all()
            db.session.commit()

    from PfaKSys.models import SystemSettings, UserGroup
    with app.app_context():
        # create missing entries
        if len(SystemSettings.query.all()) == 0:
            db.session.add(SystemSettings())

        if UserGroup.query.filter_by(name='admin').first() == None:
            db.session.add(UserGroup(name='admin'))

        db.session.commit()

        # read config from system settings
        system_settings = SystemSettings.query.first()

        for key in system_settings.mail:
            app.config[key] = system_settings.mail[key]
        for key in system_settings.calendar:
            app.config[key] = system_settings.calendar[key]

    # init mail extension
    mail.init_app(app)

    # schedule background jobs
    import PfaKSys.main.background_jobs
    scheduler.start()
    atexit.register(scheduler.shutdown)

    # import and register blueprints
    from PfaKSys.admin.routes import admin_blueprint
    from PfaKSys.data.routes import data_blueprint
    from PfaKSys.error.handlers import error_blueprint
    from PfaKSys.item.routes import item_blueprint
    from PfaKSys.main.routes import main_blueprint
    from PfaKSys.user.routes import user_blueprint

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(error_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(user_blueprint)

    @app.context_processor
    def inject_template_scope() -> dict:
        def cookies_check() -> bool:
            value = request.cookies.get('cookie_consent')
            return value == 'true'

        return {'cookies_check': cookies_check}

    app.logger.info('Server has been started successfully.')

    return app
