from enum import Enum
from functools import wraps
from flask import abort
from flask_babel import lazy_gettext
from flask_login import current_user

from PfaKSys.models import UserGroup


class Permission(Enum):
    data_export = lazy_gettext('main.permissions.data_export')
    data_import = lazy_gettext('main.permissions.data_import')
    manage_material = lazy_gettext('main.permissions.manage_material')
    manage_categories = lazy_gettext('main.permissions.manage_categories')
    manage_locations = lazy_gettext('main.permissions.manage_locations')

    @classmethod
    def __dir__(cls) -> list:
        return list(permission for permission in cls)

    @staticmethod
    def from_str(name: str):
        match name:
            case 'data_export':
                return Permission.data_export
            case 'data_import':
                return Permission.data_import
            case 'manage_material':
                return Permission.manage_material
            case 'manage_categories':
                return Permission.manage_categories
            case 'manage_locations':
                return Permission.manage_locations
            case _:
                raise ValueError(f'The permission "{name}" does not exist!')

    @staticmethod
    def from_str_list_to_value_list(permission_list: list):
        return [Permission.from_str(p).value for p in permission_list]


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if UserGroup.query.filter_by(name='admin').first() in current_user.groups:
            return func(*args, **kwargs)
        else:
            abort(403)

    return decorated_view


def permission_required(permission: Permission):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.is_admin():
                return func(*args, **kwargs)

            for group in current_user.groups:
                if group.permissions != None:
                    permissions = [Permission.from_str(p) for p in group.permissions.split(';')]

                    if permission in permissions:
                        return func(*args, **kwargs)

            abort(403)

        return decorated_view

    return decorator
