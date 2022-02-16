from flask import current_app
from flask_mail import Attachment, Message

from PfaKSys import mail


def send_email(subject: str='', body: str=None, recipients: list[str]=None, cc: list[str]=None, bcc: list[str]=None, attachments: list[Attachment]=None) -> None:
    msg = Message(
            subject=subject,
            body=body,
            sender=current_app.config['MAIL_SENDER'] 
                    if ('MAIL_SENDER' in current_app.config) and (current_app.config['MAIL_SENDER'] != None)
                    else current_app.config['MAIL_USERNAME'],
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            attachments=attachments)
    mail.send(msg)