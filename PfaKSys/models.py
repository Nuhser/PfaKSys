from datetime import datetime
from itsdangerous.jws import TimedJSONWebSignatureSerializer
from flask import current_app
from flask_login import UserMixin

from PfaKSys import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self) -> str:
        return f"User('{self.username}, '{self.email}', '{self.image_file}')"

    def get_reset_token(self, expire_sec: int=1800) -> str:
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expire_sec)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token: str):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])

        try:
            user_id = serializer.loads(token)['user_id']
            return User.query.get(user_id)
        except:
            return None

@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)