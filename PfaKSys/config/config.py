import os
import re

from logging.config import dictConfig


SQL_CONVENTIONS = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class Config():
    ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
    BABEL_DEFAULT_LOCALE = 'en'
    DEBUG = False
    LANGUAGES = {
        'de': 'Deutsch',
        'en': 'English'
    }
    MAIL_PASSWORD = os.environ.get('PFAKSYS_MAIL_PASSWORD')
    MAIL_USERNAME = os.environ.get('PFAKSYS_MAIL_USERNAME')
    NAMESPACE = 'PfaKSys'
    PORT = 5000
    SECRET_KEY = os.environ.get('PFAKSYS_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('PFAKSYS_SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_RELOADER = False

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


def init_logging() -> None:
    """
    This functions inititalizes the console and file loggers for PfaKSys. It should be called in the `__init__.py` file.
    """


    if not os.path.isdir('./PfaKSys/logs/'):
        os.mkdir('./PfaKSys/logs/')

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)s]  \t[%(filename)s -> %(funcName)s:%(lineno)d] - %(message)s'
            },
            'file_formatter': {
                'format': '%(asctime)s [%(levelname)s]  \t[%(filename)s -> %(funcName)s:%(lineno)d] - ' + re.sub(r'\033\[(\d|;)+?m', '', '%(message)s')
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
                'level': 'DEBUG'
            },
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'when': 'midnight',
                'backupCount': 14,
                'filename': 'PfaKSys/logs/PfaKSys.log',
                'formatter': 'file_formatter',
                'level': 'INFO'
            }
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    })