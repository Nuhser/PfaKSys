import os
import re

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
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
    NAMESPACE = 'PfaKSys'
    PORT = 5000
    SCHEDULER_JOBSTORES = {'sqlalchemy': SQLAlchemyJobStore(url='sqlite:///PfaKSys/db.sqlite')}
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_RELOADER = False

class ProductionConfig(Config):
    DEBUG = False
    HOST = '0.0.0.0'

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    HOST = '127.0.0.1'


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