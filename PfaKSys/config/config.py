import os

from logging.config import dictConfig


class Config():
    BABEL_DEFAULT_LOCALE = 'de'
    DEBUG_MODE = True
    LANGUAGES = {
        'de': 'Deutsch',
        'en': 'English'
    }
    MAIL_PASSWORD = os.environ.get('PFAKSYS_EMAIL_PASSWORD')
    MAIL_PORT = 587
    MAIL_SERVER = 'smtp.ionos.de'
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('PFAKSYS_EMAIL_USER')
    NAMESPACE = 'PfaKSys'
    PORT = 5000
    SECRET_KEY = os.environ.get('PFAKSYS_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('PFAKSYS_SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def init_logging() -> None:
    if not os.path.isdir('./PfaKSys/logs/'):
        os.mkdir('./PfaKSys/logs/')

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)s]  \t[%(filename)s -> %(funcName)s:%(lineno)d] - %(message)s'
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
                'formatter': 'default',
                'level': 'INFO'
            }
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    })