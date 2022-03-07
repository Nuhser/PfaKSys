import os
import shutil

from datetime import datetime
from flask import current_app

from PfaKSys import db, mail
from PfaKSys.admin.forms import DatabaseSettingsForm, MailSettingsForm, NotificationSettingsForm
from PfaKSys.main.utils import get_system_settings


def database_backup() -> str:
    backup_path = os.path.join(current_app.root_path, 'backups/db')

    # create backup folder if needed
    if not os.path.isdir(backup_path):
        os.makedirs(backup_path)

    # get max backups to keep from db
    system_settings = get_system_settings()
    backup_quantity = system_settings.database['BACKUP_QUANTITY']

    # delete backups if there are to many
    backup_list = [os.path.join(backup_path, name) for name in os.listdir(backup_path) if os.path.isfile(os.path.join(backup_path, name))]
    while len(backup_list) >= backup_quantity:
        oldest_backup = backup_list.pop(backup_list.index(min(backup_list, key=os.path.getctime)))
        os.remove(oldest_backup)

    # backup db
    new_backup_name = f'backup_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.sqlite'
    shutil.copy(os.path.join(current_app.root_path, 'db.sqlite'), os.path.join(backup_path, new_backup_name))

    return new_backup_name


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
