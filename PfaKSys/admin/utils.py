from flask import current_app

from PfaKSys import db, mail
from PfaKSys.admin.forms import DatabaseSettingsForm, MailSettingsForm, NotificationSettingsForm
from PfaKSys.main.utils import get_system_settings


def save_database_settings(form: DatabaseSettingsForm) -> None:
    system_settings = get_system_settings()
    system_settings.database = {
        'BACKUP_QUANTITY': form.database_backup_quantity.data
    }
    db.session.commit()


def save_mail_settings(form: MailSettingsForm) -> None:
    system_settings = get_system_settings()
    system_settings.mail = {
        'MAIL_SERVER': form.server.data,
        'MAIL_PORT': form.port.data,
        'MAIL_USE_TLS': form.use_tls.data,
        'MAIL_USE_SSL': form.use_ssl.data,
        'MAIL_SENDER': form.mail_sender.data
    }
    db.session.commit()

    for key in system_settings.mail:
        current_app.config[key] = system_settings.mail[key]

    mail.init_app(current_app)


def save_notification_settings(form: NotificationSettingsForm) -> None:
    get_system_settings().notifications = {
        'NEW_USER': form.new_user.data
    }
    db.session.commit()
