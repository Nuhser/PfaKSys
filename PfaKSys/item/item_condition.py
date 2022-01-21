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

    @classmethod
    def __dir__(cls) -> list:
        return list(condition for condition in cls)

    def get_condition_color(self) -> str:
        match self:
            case ItemCondition.unknown:
                return 'color: white; background-color: LightSlateGrey;'
            case ItemCondition.good:
                return 'background-color: LimeGreen;'
            case ItemCondition.ok:
                return 'background-color: Gold;'
            case ItemCondition.mostly_ok:
                return 'background-color: Orange;'
            case ItemCondition.damaged:
                return 'color: white; background-color: Tomato;'
            case ItemCondition.in_repair:
                return 'color: white; background-color: Teal;'
            case ItemCondition.unhygienic:
                return 'background-color: LightPink;'
            case ItemCondition.other:
                return 'color: white; background-color: LightSlateGrey;'
            case _:
                return ''
