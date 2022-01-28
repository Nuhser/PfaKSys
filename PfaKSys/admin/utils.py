from flask import current_app

from PfaKSys import db, mail
from PfaKSys.admin.forms import MailSettingsForm
from PfaKSys.models import SystemSettings


def save_mail_settings(form: MailSettingsForm) -> None:
    system_settings = SystemSettings.query.first()
    system_settings.mail = {
        'MAIL_SERVER': form.server.data,
        'MAIL_PORT': form.port.data,
        'MAIL_USE_TLS': form.use_tls.data,
        'MAIL_SENDER': form.sender.data
    }
    db.session.commit()

    for key in system_settings.mail:
        current_app.config[key] = system_settings.mail[key]

    mail.init_app(current_app)
