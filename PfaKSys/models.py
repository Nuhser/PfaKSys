from datetime import datetime
from itsdangerous.jws import TimedJSONWebSignatureSerializer
from flask import current_app
from flask_login import UserMixin

from PfaKSys import db, login_manager
from PfaKSys.item.item_condition import ItemCondition


user_group_association_table = db.Table('user_group_association', db.Model.metadata,
    db.Column('user_id', db.ForeignKey('user.id'), primary_key=True),
    db.Column('user_group_id', db.ForeignKey('user_group.id'), primary_key=True)
)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    count = db.Column(db.Integer, nullable=False, default=0)
    condition = db.Column(db.Enum(ItemCondition), nullable=False, default=ItemCondition.unknown)
    date_checked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)
    comment = db.Column(db.Text)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    category_id = db.Column(db.Integer, db.ForeignKey('item_category.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('item_location.id'))

    def __repr__(self) -> str:
        return f"Item('{self.name}', '{self.count}', '{self.condition}', '{self.date_checked}')"


class ItemCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    items = db.relationship('Item', backref='category')

    def __repr__(self) -> str:
        return f"ItemCategory('{self.name}')"


class ItemLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    items = db.relationship('Item', backref='location')

    def __repr__(self) -> str:
        return f"ItemLocation('{self.name}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    groups = db.relationship('UserGroup', secondary=user_group_association_table, backref='users')

    def __repr__(self) -> str:
        return f"User('{self.username}, '{self.full_name}', '{self.email}', Groups: '{self.groups}', '{self.image_file}')"

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


class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"UserGroup('{self.name}')"


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)