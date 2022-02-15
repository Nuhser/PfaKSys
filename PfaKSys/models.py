from datetime import datetime
from itsdangerous.jws import TimedJSONWebSignatureSerializer
from flask import current_app, request
from flask_login import UserMixin, current_user

from PfaKSys import db, login_manager
from PfaKSys.item.item_condition import ItemCondition


user_group_association_table = db.Table('user_group_association', db.Model.metadata,
    db.Column('user_id', db.ForeignKey('user.id'), primary_key=True),
    db.Column('user_group_id', db.ForeignKey('user_group.id'), primary_key=True)
)


# class Borrow(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date_from = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     date_to = db.Column(db.DateTime)
#     borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     borrower = db.relationship('User', backref='borrows')
    


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    has_count = db.Column(db.Boolean, nullable=False, default=True)
    count = db.Column(db.Integer, nullable=False, default=0)
    condition = db.Column(db.Enum(ItemCondition), nullable=False, default=ItemCondition.unknown)
    date_checked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)
    comment = db.Column(db.Text)
    image_files = db.Column(db.String, nullable=False, default='default.png')
    category_id = db.Column(db.Integer, db.ForeignKey('item_category.id'))
    category = db.relationship('ItemCategory', back_populates='items')
    location_id = db.Column(db.Integer, db.ForeignKey('item_location.id'))
    location = db.relationship('ItemLocation', back_populates='items')

    def __repr__(self) -> str:
        return f"Item('{self.name}', '{self.count}', '{self.condition}', '{self.date_checked}')"


class ItemCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    items = db.relationship('Item', back_populates='category')

    def __repr__(self) -> str:
        return f"ItemCategory('{self.name}')"


class ItemLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    items = db.relationship('Item', back_populates='location')

    def __repr__(self) -> str:
        return f"ItemLocation('{self.name}')"


class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calendar = db.Column(db.JSON, nullable=False, default={'CALENDAR_LINK': None, 'CALENDAR_CATEGORIES': [], 'CALENDAR_SYNC_INTERVALL': 5})
    database = db.Column(db.JSON, nullable=False, default={'BACKUP_QUANTITY': 2})
    mail = db.Column(db.JSON, nullable=False, default={'MAIL_SERVER': None, 'MAIL_PORT': 587, 'MAIL_USE_TLS': True, 'MAIL_SENDER': None})

    def __repr__(self) -> str:
        return f"SystemSettings(ID: '{self.id}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    setting_id = db.Column(db.Integer, db.ForeignKey('user_settings.id'))
    settings = db.relationship('UserSettings', backref='user')
    groups = db.relationship('UserGroup', secondary=user_group_association_table, backref='users')

    def __repr__(self) -> str:
        return f"User('{self.username}, '{self.full_name}', '{self.email}', Groups: '{self.groups}', '{self.image_file}')"

    def is_admin(self) -> bool:
        return UserGroup.query.filter_by(name='admin').first() in self.groups

    def get_reset_token(self, expire_sec: int=1800) -> str:
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expire_sec)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    def has_permission(self, permission: str):
        if current_user.is_admin():
            return True

        for group in self.groups:
            if group.permissions == None:
                return False
            if permission in group.permissions.split(';'):
                return True

        return False

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
    permissions = db.Column(db.String, default='')

    def __repr__(self) -> str:
        return f"UserGroup('{self.name}', '{self.permissions}')"


class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(2), default='de')
    item_filters = db.Column(db.JSON, default={})

    def __repr__(self) -> str:
        return f"UserSettings('{self.language}', '{self.item_filters}')"


@login_manager.user_loader
def load_user(user_id: int) -> User:
    user = User.query.get(user_id)

    if user != None and user.setting_id == None:
        user.settings = UserSettings(
                            language=request.accept_languages.best_match(current_app.config['LANGUAGES'].keys()),
                            item_filters={})
        db.session.commit()

    return user