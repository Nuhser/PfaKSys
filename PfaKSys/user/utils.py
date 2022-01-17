import hashlib
import os
import secrets
import urllib

from flask import current_app, url_for
from flask_babel import gettext
from flask_mail import Message
from PIL import Image

from PfaKSys import mail
from PfaKSys.models import User


def generate_and_save_gravatar(email: str) -> str:
    gravatar_url = 'https://www.gravatar.com/avatar/' + hashlib.md5(email.lower().encode('utf-8')).hexdigest() + '?' + urllib.parse.urlencode({'d': 'retro', 's': '125', 'r': 'g'})

    picture_name = secrets.token_hex(8) + '.png'
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_name)
    
    urllib.request.urlretrieve(gravatar_url, picture_path)
    
    return picture_name


def save_picture(form_picture) -> str:
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_name = random_hex + file_extension

    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_name)

    thumbnail = Image.open(form_picture)
    thumbnail.thumbnail((125, 125))
    thumbnail.save(picture_path)

    return picture_name


def send_reset_email(user: User) -> None:
    token = user.get_reset_token()

    msg = Message(gettext('mail.reset_password.subject'), sender='noreply@martin-immel.de', recipients=[user.email])
    msg.body = gettext('mail.reset_password.body', link=url_for('user.reset_password', token=token, _external=True))
    mail.send(msg)