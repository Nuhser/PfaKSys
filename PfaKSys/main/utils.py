from typing import Any
from flask import current_app, url_for

from PfaKSys.models import SystemSettings


def get_system_settings():
    return SystemSettings.query.first()


def _url_for(url: str, **values: Any) -> str:
    return url_for(url, _external=True, _scheme=current_app.config['URL_SCHEME'], **values)