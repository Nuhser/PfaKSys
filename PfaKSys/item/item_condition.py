from enum import Enum
from flask_babel import lazy_gettext


class ItemCondition(Enum):
    unknown = lazy_gettext('item.item_condition.unknown')
    good = lazy_gettext('item.item_condition.good')
    ok = lazy_gettext('item.item_condition.ok')
    mostly_ok = lazy_gettext('item.item_condition.mostly_ok')
    damaged = lazy_gettext('item.item_condition.damaged')
    in_repair = lazy_gettext('item.item_condition.in_repair')
    unhygienic = lazy_gettext('item.item_condition.unhygienic')
    other = lazy_gettext('item.item_condition.other')
